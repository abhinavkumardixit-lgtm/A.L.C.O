// ==============================================================================
// AeroGNN-Core ASIC: Edge Graph Neural Network Accelerator RTL
// Target Technology: TSMC 28nm HPC+ (1.0V Core, 3.3V I/O)
// Author: Abhinav Kumar Dixit (Independent Researcher, 2026)
// Project: AeroGuard-Net UAV Autonomous Aerodynamic Flight Controller
// ==============================================================================

`timescale 1ns / 1ps

module aerognn_core_accelerator #(
    parameter DATA_WIDTH      = 16,     // FP16/INT16 fixed point (Q8.8 format)
    parameter NUM_NODES       = 32,     // Maximum graph sensor/actuator nodes
    parameter FEATURE_DIM     = 16,     // Node latent state dimension
    parameter ADDR_WIDTH      = 10      // Address width for 1024-word buffer
)(
    // System Clock and Active-Low Synchronous Reset
    input  wire                   clk,
    input  wire                   rst_n,

    // Control and Status Interface (AXI4-Lite compatible)
    input  wire                   start_inference,
    output reg                    busy,
    output reg                    inference_done,
    output reg  [31:0]            cycle_count,

    // Graph Node Feature Configuration Bus
    input  wire                   cfg_we,
    input  wire [ADDR_WIDTH-1:0]  cfg_addr,
    input  wire [DATA_WIDTH-1:0]  cfg_wdata,
    output wire [DATA_WIDTH-1:0]  cfg_rdata,

    // Real-Time Pressure / Flow Sensor Inputs (Direct DMA FIFO interface)
    input  wire [NUM_NODES-1:0]   sensor_valid,
    input  wire [DATA_WIDTH-1:0]  sensor_data_in,

    // Control Output Command Bus to SJA Inverters and Elevons
    output reg  [15:0]            actuator_sja_freq_cmd,     // SJA resonant frequency (Hz)
    output reg  [15:0]            actuator_sja_cmu_cmd,      // SJA momentum coefficient C_mu
    output reg  [15:0]            elevon_pitch_trim_cmd,     // Elevon trim angle (0.01 deg)
    output reg                    alert_stall_imminent       // Hardware stall warning flag
);

    // -------------------------------------------------------------------------
    // Internal State Machine Encoding
    // -------------------------------------------------------------------------
    localparam STATE_IDLE         = 3'b000;
    localparam STATE_LOAD_SENSOR  = 3'b001;
    localparam STATE_MSG_PASSING  = 3'b010;
    localparam STATE_AGGREGATION  = 3'b011;
    localparam STATE_ACTIVATION   = 3'b100;
    localparam STATE_OUTPUT_WRITE = 3'b101;
    localparam STATE_DONE         = 3'b110;

    reg [2:0] current_state, next_state;

    // -------------------------------------------------------------------------
    // Feature Memory (SRAM Macro Model: Dual-Port, 1024 x 16-bit)
    // -------------------------------------------------------------------------
    reg [DATA_WIDTH-1:0] feature_sram [0:(1<<ADDR_WIDTH)-1];
    reg [ADDR_WIDTH-1:0] mem_raddr;
    reg [DATA_WIDTH-1:0] mem_rdata_reg;

    always @(posedge clk) begin
        if (cfg_we)
            feature_sram[cfg_addr] <= cfg_wdata;
        mem_rdata_reg <= feature_sram[mem_raddr];
    end
    assign cfg_rdata = mem_rdata_reg;

    // -------------------------------------------------------------------------
    // Systolic MAC Core (16-bit Signed Fixed Point Multiply-Accumulate)
    // -------------------------------------------------------------------------
    reg  signed [DATA_WIDTH-1:0] mac_a;
    reg  signed [DATA_WIDTH-1:0] mac_b;
    reg  signed [31:0]           mac_acc;
    wire signed [31:0]           mult_result = mac_a * mac_b;

    // Graph Traversal Iterators
    reg [4:0] node_idx;
    reg [4:0] neighbor_idx;
    reg [3:0] feat_idx;
    reg [7:0] layer_step;

    // Fixed-point LeakyReLU Hardware Activation: f(x) = (x >= 0) ? x : (x >>> 3)  (alpha = 0.125)
    function signed [DATA_WIDTH-1:0] leaky_relu;
        input signed [DATA_WIDTH-1:0] in_val;
        begin
            if (in_val[DATA_WIDTH-1] == 1'b0) // Positive
                leaky_relu = in_val;
            else                              // Negative: multiply by 0.125 via shift
                leaky_relu = in_val >>> 3;
        end
    endfunction

    // -------------------------------------------------------------------------
    // Sequential State Machine & Latency Counter
    // -------------------------------------------------------------------------
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_state         <= STATE_IDLE;
            cycle_count           <= 32'd0;
            busy                  <= 1'b0;
            inference_done        <= 1'b0;
            node_idx              <= 5'd0;
            neighbor_idx          <= 5'd0;
            feat_idx              <= 4'd0;
            layer_step            <= 8'd0;
            mac_acc               <= 32'sd0;
            actuator_sja_freq_cmd <= 16'd460;
            actuator_sja_cmu_cmd  <= 16'd55;
            elevon_pitch_trim_cmd <= 16'd0;
            alert_stall_imminent  <= 1'b0;
        end else begin
            current_state <= next_state;

            if (busy)
                cycle_count <= cycle_count + 1'b1;
            else if (start_inference)
                cycle_count <= 32'd0;

            case (current_state)
                STATE_IDLE: begin
                    busy           <= 1'b0;
                    inference_done <= 1'b0;
                    if (start_inference) begin
                        busy       <= 1'b1;
                        node_idx   <= 5'd0;
                        layer_step <= 8'd0;
                    end
                end

                STATE_LOAD_SENSOR: begin
                    // Latch real-time pressure sensor field into active state
                    feature_sram[node_idx] <= sensor_data_in;
                    if (node_idx == NUM_NODES - 1) begin
                        node_idx     <= 5'd0;
                        neighbor_idx <= 5'd0;
                        feat_idx     <= 4'd0;
                    end else begin
                        node_idx <= node_idx + 1'b1;
                    end
                end

                STATE_MSG_PASSING: begin
                    // Sparse Edge Feature Message Computation: h_j * W_edge
                    mac_a   <= feature_sram[neighbor_idx];
                    mac_b   <= 16'sh0180; // Pre-programmed edge weight W = 1.50 in Q8.8
                    mac_acc <= mac_acc + mult_result;
                end

                STATE_AGGREGATION: begin
                    // Sum aggregation over localized 4-neighborhood graph topology
                    if (neighbor_idx == 5'd3) begin
                        neighbor_idx <= 5'd0;
                    end else begin
                        neighbor_idx <= neighbor_idx + 1'b1;
                    end
                end

                STATE_ACTIVATION: begin
                    // Apply hardware activation and store updated latent vector
                    feature_sram[node_idx] <= leaky_relu(mac_acc[23:8]);
                    mac_acc <= 32'sd0;

                    if (node_idx == NUM_NODES - 1) begin
                        node_idx <= 5'd0;
                        layer_step <= layer_step + 1'b1;
                    end else begin
                        node_idx <= node_idx + 1'b1;
                    end
                end

                STATE_OUTPUT_WRITE: begin
                    // Project final layer representation to aerodynamic actuation commands
                    // Output 1: SJA Resonant Frequency: 450Hz + bias
                    actuator_sja_freq_cmd <= 16'd450 + {12'd0, feature_sram[0][7:4]};
                    // Output 2: SJA Momentum C_mu (scaled x1000): 0.055
                    actuator_sja_cmu_cmd  <= 16'd55  + {12'd0, feature_sram[1][5:2]};
                    // Output 3: Elevon Pitch Trim (0.01 deg units)
                    elevon_pitch_trim_cmd <= {{8{feature_sram[2][15]}}, feature_sram[2][15:8]};

                    // Detect aerodynamic separation signature: pressure drop on suction peak
                    if (feature_sram[4] > 16'sh0800) // Suction collapse indicator
                        alert_stall_imminent <= 1'b1;
                    else
                        alert_stall_imminent <= 1'b0;
                end

                STATE_DONE: begin
                    busy           <= 1'b0;
                    inference_done <= 1'b1;
                end
            endcase
        end
    end

    // -------------------------------------------------------------------------
    // Combinational Next State Logic
    // -------------------------------------------------------------------------
    always @(*) begin
        case (current_state)
            STATE_IDLE:
                next_state = start_inference ? STATE_LOAD_SENSOR : STATE_IDLE;
            STATE_LOAD_SENSOR:
                next_state = (node_idx == NUM_NODES - 1) ? STATE_MSG_PASSING : STATE_LOAD_SENSOR;
            STATE_MSG_PASSING:
                next_state = STATE_AGGREGATION;
            STATE_AGGREGATION:
                next_state = (neighbor_idx == 5'd3) ? STATE_ACTIVATION : STATE_MSG_PASSING;
            STATE_ACTIVATION: begin
                if (node_idx == NUM_NODES - 1 && layer_step == 8'd2)
                    next_state = STATE_OUTPUT_WRITE;
                else
                    next_state = STATE_MSG_PASSING;
            end
            STATE_OUTPUT_WRITE:
                next_state = STATE_DONE;
            STATE_DONE:
                next_state = STATE_IDLE;
            default:
                next_state = STATE_IDLE;
        endcase
    end

endmodule

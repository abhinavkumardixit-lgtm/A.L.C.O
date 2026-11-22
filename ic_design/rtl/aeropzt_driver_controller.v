// ==============================================================================
// AeroPZT-Driver ASIC: High-Voltage Resonant Piezoelectric Controller RTL
// Target Technology: TSMC 0.18um BCD (Bipolar-CMOS-DMOS 250V High-Voltage)
// Author: Abhinav Kumar Dixit (Independent Researcher, 2026)
// Project: AeroGuard-Net UAV Synthetic Jet Actuator (SJA) Turbulence Engine
// ==============================================================================

`timescale 1ns / 1ps

module aeropzt_driver_controller #(
    parameter CLK_FREQ_HZ     = 50000000, // 50 MHz Master Clock
    parameter DEFAULT_FREQ_HZ = 460       // 460 Hz SJA Cavity Acoustic Resonance
)(
    input  wire        clk,
    input  wire        rst_n,

    // Command Bus from AeroGNN / FMC (CAN-FD or Serial Interface)
    input  wire        cmd_enable,
    input  wire [15:0] target_freq_hz,     // Programmable resonance tuning (400-500 Hz)
    input  wire [7:0]  intensity_duty_pct, // Zero-net-mass-flux amplitude modulation (0-100%)

    // Mixed-Signal Current-Sense Feedback from High-Voltage Shunt (PLL Resonance Tracker)
    input  wire        zero_crossing_detect,
    input  wire        overcurrent_trip_n, // Hardware fast shutdown pin (< 50ns)
    input  wire        overtemp_fault_n,

    // High-Voltage DMOS Gate Drive Signals (Push-Pull Dual Half-Bridge Stage)
    output reg         gate_high_side_a,
    output reg         gate_low_side_a,
    output reg         gate_high_side_b,
    output reg         gate_low_side_b,

    // Status Telemetry Bus
    output reg  [15:0] measured_resonance_hz,
    output reg         pll_locked,
    output reg         fault_active
);

    // Dead-Time Generator: Prevents Shoot-Through Cross Conduction (200ns dead time @ 50MHz = 10 cycles)
    localparam DEAD_TIME_CYCLES = 10;

    // Period calculation: clk_ticks = CLK_FREQ_HZ / target_freq
    reg [23:0] half_period_ticks;
    reg [23:0] timer_counter;
    reg        half_cycle_phase;
    reg [7:0]  dead_time_counter;
    reg        dead_time_active;

    // Phase Locked Loop (PLL) Phase Detector Counter
    reg [23:0] pll_period_accumulator;
    reg [3:0]  pll_sample_count;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            half_period_ticks      <= CLK_FREQ_HZ / (DEFAULT_FREQ_HZ * 2);
            timer_counter          <= 24'd0;
            half_cycle_phase       <= 1'b0;
            dead_time_counter      <= 8'd0;
            dead_time_active       <= 1'b1;
            gate_high_side_a       <= 1'b0;
            gate_low_side_a        <= 1'b0;
            gate_high_side_b       <= 1'b0;
            gate_low_side_b        <= 1'b0;
            measured_resonance_hz  <= DEFAULT_FREQ_HZ;
            pll_locked             <= 1'b0;
            fault_active           <= 1'b0;
            pll_period_accumulator <= 24'd0;
            pll_sample_count       <= 4'd0;
        end else begin
            // Safety Hardware Interlock: Immediate shutdown on overcurrent or overtemperature
            if (!overcurrent_trip_n || !overtemp_fault_n) begin
                gate_high_side_a <= 1'b0;
                gate_low_side_a  <= 1'b0;
                gate_high_side_b <= 1'b0;
                gate_low_side_b  <= 1'b0;
                fault_active     <= 1'b1;
            end else if (cmd_enable) begin
                fault_active <= 1'b0;

                // Dynamic Frequency Tuning from Host or Auto-Resonant PLL
                if (target_freq_hz >= 16'd350 && target_freq_hz <= 16'd550)
                    half_period_ticks <= CLK_FREQ_HZ / (target_freq_hz * 2);

                // PWM Timer and Commutation Counter
                if (timer_counter >= half_period_ticks) begin
                    timer_counter    <= 24'd0;
                    half_cycle_phase <= ~half_cycle_phase;
                    dead_time_active <= 1'b1;
                    dead_time_counter <= 8'd0;
                    // Blank all gate drives during commutation
                    gate_high_side_a <= 1'b0;
                    gate_low_side_a  <= 1'b0;
                    gate_high_side_b <= 1'b0;
                    gate_low_side_b  <= 1'b0;
                end else begin
                    timer_counter <= timer_counter + 1'b1;

                    // Enforce Non-Overlapping Dead Time
                    if (dead_time_active) begin
                        if (dead_time_counter >= DEAD_TIME_CYCLES) begin
                            dead_time_active <= 1'b0;
                        end else begin
                            dead_time_counter <= dead_time_counter + 1'b1;
                        end
                    end else begin
                        // Active Push-Pull Output State (Drive Piezo Chamber to +200V / -200V differential)
                        if (half_cycle_phase == 1'b0) begin
                            gate_high_side_a <= 1'b1;
                            gate_low_side_a  <= 1'b0;
                            gate_high_side_b <= 1'b0;
                            gate_low_side_b  <= 1'b1;
                        end else begin
                            gate_high_side_a <= 1'b0;
                            gate_low_side_a  <= 1'b1;
                            gate_high_side_b <= 1'b1;
                            gate_low_side_b  <= 1'b0;
                        end
                    end
                end

                // PLL Tracking: measure zero-crossing interval
                if (zero_crossing_detect) begin
                    pll_period_accumulator <= pll_period_accumulator + timer_counter;
                    pll_sample_count <= pll_sample_count + 1'b1;
                    if (pll_sample_count == 4'd15) begin
                        measured_resonance_hz <= CLK_FREQ_HZ / (pll_period_accumulator >> 3);
                        pll_period_accumulator <= 24'd0;
                        pll_sample_count <= 4'd0;
                        pll_locked <= 1'b1;
                    end
                end
            end else begin
                // Driver Disabled (Low power standby mode)
                gate_high_side_a <= 1'b0;
                gate_low_side_a  <= 1'b0;
                gate_high_side_b <= 1'b0;
                gate_low_side_b  <= 1'b0;
            end
        end
    end

endmodule

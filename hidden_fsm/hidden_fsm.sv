module hidden_fsm (
    input logic clk,
    input logic data_avail,
    output logic buf_en,
    output logic [1:0] out_sel,
    output logic out_writing
);
    
    // State encoding
    typedef enum logic [2:0] {
        A = 3'b000,  // State 0
        B = 3'b001,  // State 1
        C = 3'b010,  // State 2
        D = 3'b011,  // State 3
        E = 3'b100,  // State 4
        INVALID1 = 3'b101,  // State 5 (Invalid)
        INVALID2 = 3'b110,  // State 6 (Invalid)
        INVALID3 = 3'b111   // State 7 (Invalid)
    } state_t;
    
    state_t cur_state, next_state;
    
    // State register
    always_ff @(posedge clk) begin
        cur_state <= next_state;
    end
    
    // Next state logic
    always_comb begin
        case (cur_state)
            A: begin
                if (data_avail)
                    next_state = E;
                else
                    next_state = A;
            end
            
            B: begin
                next_state = C;
            end
            
            C: begin
                next_state = D;
            end
            
            D: begin
                if (data_avail)
                    next_state = E;
                else
                    next_state = A;
            end
            
            E: begin
                next_state = B;
            end
            
            // Invalid states transition to themselves
            INVALID1: begin
                next_state = INVALID1;
            end
            
            INVALID2: begin
                next_state = INVALID2;
            end
            
            INVALID3: begin
                next_state = INVALID3;
            end
            
            default: begin
                next_state = A;
            end
        endcase
    end
    
    // Output logic (Moore machine)
    always_comb begin
        // Default outputs
        buf_en = 1'b0;
        out_sel = 2'b00;
        out_writing = 1'b0;
        
        case (cur_state)
            A: begin
                buf_en = 1'b0;
                out_sel = 2'b01;
                out_writing = 1'b1;
            end
            
            B: begin
                buf_en = 1'b0;
                out_sel = 2'b11;
                out_writing = 1'b1;
            end
            
            C: begin
                buf_en = 1'b1;
                out_sel = 2'b00;
                out_writing = 1'b0;
            end
            
            D: begin
                buf_en = 1'b0;
                out_sel = 2'b01;
                out_writing = 1'b1;
            end
            
            E: begin
                buf_en = 1'b0;
                out_sel = 2'b10;
                out_writing = 1'b1;
            end
            
            // Invalid states have specific outputs (matching test results)
            INVALID1, INVALID2, INVALID3: begin
                buf_en = 1'b0;
                out_sel = 2'b00;
                out_writing = 1'b0;
            end
            
            default: begin
                buf_en = 1'b0;
                out_sel = 2'b00;
                out_writing = 1'b0;
            end
        endcase
    end
    
endmodule
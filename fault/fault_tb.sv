module testbench;
  logic a, b, c, d;
  logic x;
  
  fault dut(.a(a), .b(b), .c(c), .d(d), .x(x));
  
  logic [3:0] input_vectors[7] = '{
    4'b0000,
    4'b0001,
    4'b0010,
    4'b0011,
    4'b0100,
    4'b1000,
    4'b1100
  };
  
  logic expected_outputs[7] = '{
    1'b1, // 0000
    1'b1, // 0001
    1'b0, // 0010
    1'b1, // 0011
    1'b0, // 0100
    1'b0, // 1000
    1'b1  // 1100
  };
  
  string fault_descriptions[7] = '{
    "a-SA1, N1-SA0, N3-SA0", // 0000
    "N4-SA0, x-SA0",         // 0001
    "d-SA1, N3-SA1, N4-SA1", // 0010
    "d-SA0",                 // 0011
    "b-SA0",                 // 0100
    "a-SA0, N1-SA1, N2-SA1, x-SA1", // 1000
    "N2-SA0"                 // 1100
  };
  
  string detected_faults[$];
  
  initial begin
    $display("Starting testbench for fault detection...");
    $display("Running test vectors to identify possible faults");
    $display("------------------------------------------------");
    
    for (int i = 0; i < 7; i++) begin
      {a, b, c, d} = input_vectors[i];
      
      #10;
      
      if (x !== expected_outputs[i]) begin
        $display("Test vector %b failed: expected x=%b, got x=%b", 
                 input_vectors[i], expected_outputs[i], x);
        $display("Possible faults: %s", fault_descriptions[i]);
        
        detected_faults.push_back(fault_descriptions[i]);
      end else begin
        $display("Test vector %b passed: x=%b", input_vectors[i], x);
      end
    end
    
    $display("\n------------------------------------------------");
    $display("Test Results Summary:");
    
    if (detected_faults.size() == 0) begin
      $display("No faults detected. Circuit appears to be working correctly.");
    end else begin
      $display("Detected faults in circuit!");
      $display("All possible faults based on failed test vectors:");
      
      foreach (detected_faults[i]) begin
        $display("- %s", detected_faults[i]);
      end
    end
    
    $finish;
  end
endmodule
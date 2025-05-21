function Latency_Capacity(h_freq, transmit_power, NFig, temperature, p_BS, p_UE, Bits, Bitssymb, K, deltaf)
    
    % Latency

    c = 2.99792458*10^8; % Speed of light in air [m/s]
    d = sqrt((p_BS(1)-p_UE(1))^2+(p_BS(2)-p_UE(2))^2+(p_BS(3)-p_UE(3))^2); % Euclidean distance [m]
    Dpr = d/c; % Propagation Delay [s] % Time taken for packet to cross transmission medium (distance/speed of packet)
    
    %should it be Bits or Nbits ?
    Dt = ceil((Bits/(Bitssymb*K)))*(1/deltaf); % Transmission Delay [s] % Time to push data in transmission medium or wire.
    % QPSK 2bits/symbol
    
    % Capacity
    h_freq_combined = [];
    s = size(h_freq);
    for i = 2:2:s(2)
         h_freq_combined = [h_freq_combined, h_freq(:,i-1)+h_freq(:,i)];
    end

    h_freq = mean(abs(h_freq_combined),2);


    BW = K*deltaf; % Bandwidth [Hz] % BW=K*deltaf ?
    transmit_power = db2pow(transmit_power)/1000; % [W]
    avg_transmit_power = transmit_power/K;
    NF = 10^(NFig/10); 
    sigma2 = 1.380649*10^-23*temperature*NF; % The noise of the signal (add noise figure)

    SNR = (h_freq.^2.*avg_transmit_power)/(sigma2*deltaf); % We get h_freq from Sionna
    
    C = 0;

    for k = 1:1:K
        C = C + deltaf*log2(1+SNR(k));
    end
    
    
        
        
    Latency = Dpr + Dt; % [s] % is the transmission delay supposed to be 1/SCS or Nsub_carriers/BW ?
    Capacity = C; % [bits/s] sum over all Sub carriers
    

    % Coverage map
    %done by plotting the PEB for all x and y positions


end
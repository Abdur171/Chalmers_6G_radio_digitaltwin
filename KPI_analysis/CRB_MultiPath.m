function PEB = CRB_MultiPath(power,carrier_frequency, SCS, K, L, p_BS, p_UE, yaw, pitch, roll, ant_posTX, alfa_sionna, tau, theta_local, phi_local) %angleA, elevationA, angleD, elevationD
    rng(2)

    alfa_combined = [];
    for v = 2:2:8
        complex = alfa_sionna(:,v-1) + 1j*alfa_sionna(:,v);
        alfa_combined = [alfa_combined, complex];
    end

    % Putting the line-of-sight path values in the first row for every
    % parameter
    [a b] = min(tau);
    if b~=1, tau([1 b]) = tau([b 1]); theta_local([1 b]) = theta_local([b 1]); phi_local([1 b]) = phi_local([b 1]); alfa_combined([1 b],:) = alfa_combined([b 1],:); end


    clock = 0; %10^-8;
    c = 2.99792458*10^8;
    d = sqrt((p_BS(1)-p_UE(1))^2+(p_BS(2)-p_UE(2))^2+(p_BS(3)-p_UE(3))^2);
    lambda = c/carrier_frequency;
    NPSD = 1.380649*10^-23*290;
    NFig = 7; 
    NF = 10^(NFig/10);
    sigma = sqrt(NPSD*NF);
    G = length(theta_local);
    Ntx = length(ant_posTX);
    rotation_matrix = [cosd(yaw) -sind(yaw) 0;
                       sind(yaw) cosd(yaw) 0;
                       0 0 1] * [1 0 0;
                        0 cosd(pitch) -sind(pitch);
                        0 sind(pitch) cosd(pitch)] * [cosd(roll) 0 sind(roll);
                        0 1 0;
                        -sind(roll) 0 cosd(roll)];

    num = transpose(rotation_matrix)*transpose((p_UE-p_BS));

    u = @(theta,phi)[cos(theta).*sin(phi);
               cos(theta).*sin(phi);
               sin(phi)];

  % 1) Add f_l to the model, N_tx by L matrix, random e^(-j2pifc(uniform random 0-2pi))
  % 2) Remove the third loop
  % 3) Add x (complex TX symbol which has the magnitude of tx power)
  Tx_power = db2pow(power)/1000; % 24 dBm -> Watt;
  x = sqrt(Tx_power/(K*SCS*Ntx)); % !!! added Ntx to denomenator % magnitude of energy
  
  rand_tau = rand(Ntx,L); %!!! randn -> rand (from normal dist. to uniform)
  f_l = exp(-j*2*pi*rand_tau); %!!! removed fc because it is not needed (we just need a random number from 0 to 1) % Generated a random f_l matrix with dimension 4x14 (4 tx antenna positions and 14 OFDM symbols) 
 
    %alfa = lambda/(4*pi*d); % The Gtx and Grx have both been set to 1 as we assume the emitted power is the same from every angle of the base station
    %tau = d/c+clock; 
    %aTX = exp(-j*2*pi*carrier_frequency*ant_posTX*u(theta_local,phi_local)/c); %Unsure
    
    

    alfa1 = mean(abs(alfa_combined),2);

    %tau = [3.9257588e-07];

    alfa_phase = exp(-j*2*pi*carrier_frequency*tau);
    alfa=alfa1.*alfa_phase;

    aTX = alfa_combined./alfa;

    list = zeros(5*G,5*G); %replace length of theta_local with G

    for k = 0:1:K-1
        for l = 0:1:L-1
            %for n = 1:1:Ntx
            derivatives = [];
                for g = 1:1:G
                    
                    dYdAr = x*exp(-j*2*pi*k*SCS*tau(g))*aTX(g,:)*f_l(:,l+1); % Now we only use one column in f_l at a time when performing the matrix multiplication 
                    dYdAi = 1j*x*exp(-j*2*pi*k*SCS*tau(g))*aTX(g,:)*f_l(:,l+1);
                    dYdT = x*-j*2*pi*k*SCS*alfa(g)*exp(-j*2*pi*k*SCS*tau(g))*aTX(g,:)*f_l(:,l+1);
            
                    dYdTheta_localTX = x*alfa(g)*exp(-j*2*pi*(k*SCS)*tau(g))*(-j*2*pi*carrier_frequency)/c*transpose((ant_posTX*[-sin(theta_local(g))*sin(phi_local(g)); ...
                                                                                                                                 cos(theta_local(g))*sin(phi_local(g)); ...
                                                                                                                                                  0])).*aTX(g,:)*f_l(:,l+1);
                    dYdPhi_localTX = x*alfa(g)*exp(-j*2*pi*(k*SCS)*tau(g))*(-j*2*pi*carrier_frequency)/c*transpose((ant_posTX*[cos(theta_local(g))*cos(phi_local(g)); ...
                                                                                                                               sin(theta_local(g))*cos(phi_local(g)); ...
                                                                                                                               -sin(phi_local(g))])).*aTX(g,:)*f_l(:,l+1);
            
                    derivatives = [derivatives, dYdAr, dYdAi, dYdT, dYdTheta_localTX, dYdPhi_localTX];
                end


                dt = transpose(derivatives);
                cdt = conj(dt);
                Fisher = 2/sigma^2*real(cdt*derivatives);

                list = list + Fisher;
            %end
        end
    end
        

        
    %n2 = [a1real, a1imag, x, y, z, a2real, a2imag, tau2, theta2, phi2]; %!!! added alpha and removed clock bias from the model
    
    dArdAr = 1; % !!! brought this back
    dArdAi = 0; % j*a_imag
    dArdX = 0; % !!!-(lambda*(p_UE(1)-p_BS(1)))/(4*pi*d^3); Although alpha (aka alfa) depends on position, we dont usually use it for positioning, so we should not unpackage it and keep it as is
    dArdY = 0; % !!!-(lambda*(p_UE(2)-p_BS(2)))/(4*pi*d^3);
    dArdZ = 0; % !!!-(lambda*(p_UE(3)-p_BS(3)))/(4*pi*d^3);
%     dAdClock = 0; %!!!

    dAidAr = 0; % !!! brought this back
    dAidAi = 1; % j*a_imag
    dAidX = 0; % !!!-(lambda*(p_UE(1)-p_BS(1)))/(4*pi*d^3); Although alpha (aka alfa) depends on position, we dont usually use it for positioning, so we should not unpackage it and keep it as is
    dAidY = 0; % !!!-(lambda*(p_UE(2)-p_BS(2)))/(4*pi*d^3);
    dAidZ = 0;

    
    dTdAr = 0; %!!! brought this back
    dTdAi = 0;
    dTdX = (p_UE(1)-p_BS(1))/(c*d);  
    dTdY = (p_UE(2)-p_BS(2))/(c*d);    
    dTdZ = (p_UE(3)-p_BS(3))/(c*d);
%     dTdClock = 1; %!!! commented
    
    k1 = num(2)/num(1);
    k2 = num(3)/d;
    
    dThetadAr = 0; %!!! brought this back
    dThetadAi = 0;
    dThetadX = (1/(1+k1^2))*((rotation_matrix(1,2)*num(1) - num(2)*rotation_matrix(1,1)) / num(1)^2); %!!! rotation_matrix(2,1) -> rotation_matrix(1,2)
    dThetadY = (1/(1+k1^2))*((rotation_matrix(2,2)*num(1) - num(2)*rotation_matrix(2,1)) / num(1)^2); %!!! rotation_matrix(2,1) -> rotation_matrix(1,2)
    dThetadZ = (1/(1+k1^2))*((rotation_matrix(3,2)*num(1) - num(2)*rotation_matrix(3,1)) / num(1)^2); %!!! rotation_matrix(2,3) -> rotation_matrix(3,2) ... and rotation_matrix(1,3) -> rotation_matrix(3,1)
%     dThetadClock = 0; %!!! commented
    
    dPhidAr = 0; %!!! brought this back
    dPhidAi = 0;
    dPhidX = -(1/sqrt(1-k2^2))*((rotation_matrix(1,3)*d - num(3)*(p_UE(1)-p_BS(1))/d) / d^2); %!!! rotation_matrix(3,1) -> rotation_matrix(1,3)
    dPhidY = -(1/sqrt(1-k2^2))*((rotation_matrix(2,3)*d - num(3)*(p_UE(2)-p_BS(2))/d) / d^2); %!!! rotation_matrix(3,2) -> rotation_matrix(2,3)
    dPhidZ = -(1/sqrt(1-k2^2))*((rotation_matrix(3,3)*d - num(3)*(p_UE(3)-p_BS(3))/d) / d^2); 
%     dPhidClock = 0; %!!! commented
    
        
    

    T1 = [dArdAr dArdAi dArdX dArdY dArdZ;                                                                      % dAdClock; %!!! Removed clock bias from the model
          dAidAr dAidAi dAidX dAidY dAidZ;
          dTdAr dTdAi dTdX dTdY dTdZ;% dTdClock; %!!!
          dThetadAr dThetadAi dThetadX dThetadY dThetadZ;% dThetadClock; %!!!
          dPhidAr dPhidAi dPhidX dPhidY dPhidZ];% dPhidClock]; %!!!
    
    T2 = eye(5*(length(theta_local)-1));

    T = blkdiag(T1,T2); % To combine the original Jacobian matrix with the new one (an identity matrix now since we dropped all the parameters from all paths except for the LoS path)
        
    new_Fisher = transpose(T)*list*T;


   
    CRLB = inv(list);
    boundA = sqrt(CRLB(1,1)); % Taking square root to get the standard deviation, because now we have the variance 
    boundT = sqrt(CRLB(2,2));
    boundthetaTX = sqrt(CRLB(3,3));
    boundphiTX = sqrt(CRLB(4,4));

    
    CRLB_PEB = inv(new_Fisher);
    PEB = sqrt(CRLB_PEB(3,3)+CRLB_PEB(4,4)+CRLB_PEB(5,5));

end
clc; 
clear all; %%File reading 
filename = '1m_xpositive_fast_test.csv'; num = csvread(filename,1); 
time=[];  u=[];   k=[];
u1=[];  u2=[];  u3=[]; 
n = 274;
for i = 1:1:n 
    time(i) = num(i); 
    u1(i) = num(i+n); 
    u2(i) = num(i+(2*n)); 
    u3(i) = num(i+(3*n));
end
time = time';  u1 = u1';  u2 = u2';  u3 = u3'; 
for t=1:1:n     
    if (u1(t)<0)         
        u1(t) = u1(t)*(-1);     
    else         
        u1(t) = u1(t);     
    end 
end

for t=1:1:n     
    if (u2(t)<0)         
        u2(t) = u2(t)*(-1);     
    else         
        u2(t) = u2(t);     
    end 
end 
for t=1:1:n     
    if (u3(t)<0)         
        u3(t) = u3(t)*(-1);     
    else         
        u3(t) = u3(t);     
    end 
end 

%% define our meta - variables 
duration = size(time); %how long the simulation is 
dt = 0.1;          %10 Hz continuously looking for measurement   
%% define update equations 
A = [1 dt dt^2/2;0 1 dt;0   0 1];   %transistion matrix 
B = 0;              
H = [1 0 0;0 1 0;0 0 1];     %genral form matrices ; measuremnet matrix  
%% define main variables 
u=0; 
k1 = [u1 u2 u3];              %control vector ; acceleration matrix 
Q= [0; 0; 0];                  %initized state ; [position velocity] 
Q_estimate = Q; 
P = eye(3);         % q --> estimated process error covariance. 
Ex = eye(3);                  %estimate of initial object position 
R = [1 0 0 ;0 1 0;0 0 1]; 
%% Initialize result variables 
Z_p = [];    Z_v = [];    Z_a = []; 

x_estimate_az = [];  y_estimate_az = [];  z_estimate_az =[];  %estimate of the object path using Kalman filter  
u3_bias=[];   u3_perfect =[]; 
ll = mean(u3);  
 %taking the mean of u3 will give the value and it is subtracted from 
%each u3 to find bias and u3_perfect is calculated.

for t = 1:1:duration     
    u3_bias(t) = u3(t)-ll;     
    u3_perfect(t) = u3(t)-u3_bias(t); 
end 

%% Kalman Filter for Z 
Q_estimate= [0; 0; 0];  
for t = 1:1:duration 
    % Predict     
    % Predicted State     
    Q_estimate_curr = A * Q_estimate + B * u;    %-----------1     
    Z_p = [Z_p; Q_estimate_curr(1)];     
    Z_v = [Z_v; Q_estimate_curr(2)];     
    Z_a = [Z_a; Q_estimate_curr(3)];      
    %predicted next covariance     
    P = A * P * A' + Ex;                         %-----------2 
% Update     
    %Kalman Gain     
    K = P*H'*inv(H*P*H'+R);                          %-----------3

    % Update the state estimate.     
    y = [Q_estimate_curr(1);Q_estimate_curr(2);u3(t)];      
    Q_estimate = Q_estimate_curr + K * (y - H * Q_estimate_curr); %--4 
     
    % update covariance estimation.     
    P =  (eye(3)-K*H)*P;         %-----------5 
% Store for Plotting 
    x_estimate_az = [x_estimate_az; Q_estimate(1)];     
    y_estimate_az = [y_estimate_az; Q_estimate(2)];     
    z_estimate_az = [z_estimate_az; Q_estimate(3)]; 
end 

%% Plotting 
tt = 1:1:duration; 
%x 
figure; 
hold on 
grid on 
plot(time(tt),Z_v,'-b.'); 
plot(time(tt),y_estimate_az,'-r.'); 
title('Velocity - Z axis'); 
xlabel('Time (s)'); 
ylabel ('Measured Values (m/s)');  
hold off 
  
figure; 
hold on 
grid on 
plot(time(tt),Z_p,'-r.'); 
plot(time(tt),x_estimate_az,'-b.'); 
title('Distance - Z axis');  
xlabel('Time (s)'); 
ylabel ('Measured Values (m)');  
hold off 

figure; 
hold on 
grid on 
plot(time(tt),u3(tt),'-b.'); 
plot(time(tt),z_estimate_az,'-r.'); 
title('acceleration Z axis - Comparison of actual and estimated value');                   
xlabel('Time (s)'); 
ylabel ('Measured Values (m/s^-^2)');  
hold off
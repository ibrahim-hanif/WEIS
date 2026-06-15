% EOG generator according to IEC 61400-1
% Hub-height deterministic wind time series for OpenFAST / InflowWind

cd('C:\Users\felixcme\OneDrive - NTNU\PostDoc\MADE4WIND\04_OpenFAST\IEA_15MW_TLP_NTM\wind_files\EOG_DLC4_2')
clear; clc; close all;

%% ---- Inputs ----
RefHt = 150.0;       % hub height [m]
D     = 240.0;       % rotor diameter [m]

Tg    = 10.5;        % IEC EOG duration [s]
tEnd  = 300.0;       % total simulation length [s]
dt    = 0.05;        % time step [s]
PLexp = 0.20;        % power law exponent

Vhubs   = [25];   % hub-height mean wind speeds [m/s]
tStarts = [60];   % gust start times [s]

% IEC turbulence classes and site-specific 50-year extreme wind speeds
sites = struct( ...
    'name',  {'Calabria', 'Utsira'}, ...
    'Iref',  {0.14,       0.12}, ...
    'class', {'B',        'C'}, ...
    'Ve50',  {33.0,       34.0} ...
);

%% ---- IEC parameters ----
b = 5.6;             % [m/s]
Lambda1 = 42.0;     % z_hub >= 60 m

%% ---- Time vector ----
t = (0:dt:tEnd).';

%% ---- Combined plot ----
figure; hold on; grid on;
title('IEC 61400-1 Extreme Operating Gust Profiles');
xlabel('Time [s]');
ylabel('Hub-height wind speed [m/s]');

%% ---- Loop over sites, wind speeds, and gust starts ----
for iSite = 1:length(sites)

    siteName = sites(iSite).name;
    Iref = sites(iSite).Iref;
    turbClass = sites(iSite).class;

    Ve50 = sites(iSite).Ve50;
    Ve1  = 0.8 * Ve50;

    for iV = 1:length(Vhubs)

        Vhub = Vhubs(iV);

        % IEC Eq. (10)
        sigma1 = Iref * (0.75 * Vhub + b);

        % IEC Eq. (18)
        Vgust = min( ...
            1.35 * (Ve1 - Vhub), ...
            3.3 * sigma1 / (1 + 0.1 * (D / Lambda1)) ...
        );

        fprintf('\n%s | Class %s | Vhub = %.1f m/s\n', siteName, turbClass, Vhub);
        fprintf('Ve50   = %.3f m/s\n', Ve50);
        fprintf('Ve1    = %.3f m/s\n', Ve1);
        fprintf('sigma1 = %.3f m/s\n', sigma1);
        fprintf('Vgust  = %.3f m/s\n', Vgust);

        for iS = 1:length(tStarts)

            tStart = tStarts(iS);

            V = Vhub * ones(size(t));

            ix = (t >= tStart) & (t <= tStart + Tg);
            tau = t(ix) - tStart;

            V(ix) = Vhub ...
                - 0.37 * Vgust ...
                .* sin(3 * pi * tau / Tg) ...
                .* (1 - cos(2 * pi * tau / Tg));

            Dir = zeros(size(t));

            plot( ...
                t, V, ...
                'LineWidth', 1.2, ...
                'DisplayName', sprintf('%s | Class %s | Ve50 %.0f | WS %.0f | S%d', ...
                siteName, turbClass, Ve50, Vhub, iS) ...
            );

            fname = sprintf('%s_WS%d_S%d_EOG.wnd', ...
                lower(siteName), Vhub, iS);

            fid = fopen(fname, 'w', 'n', 'US-ASCII');

            fprintf(fid, '! OpenFAST Deterministic Wind File\n');
            fprintf(fid, '! IEC 61400-1 Extreme Operating Gust, DLC 4.2\n');
            fprintf(fid, '! Site: %s | Turbulence class: %s | Iref = %.3f\n', ...
                siteName, turbClass, Iref);
            fprintf(fid, '! Vhub = %.2f m/s | Vgust = %.3f m/s | tStart = %.2f s | T = %.2f s\n', ...
                Vhub, Vgust, tStart, Tg);
            fprintf(fid, '! RefHt = %.2f m | D = %.2f m | Ve50 = %.2f m/s | Ve1 = %.2f m/s\n', ...
                RefHt, D, Ve50, Ve1);
            fprintf(fid, '! Columns: Time[s] WindSpd[m/s] WindDir[deg] VertSpd[m/s] HorShr[1/s] PLexp LinShr[1/s] Gust[m/s] Upflow[deg]\n');

            for i = 1:length(t)
                fprintf(fid, '%10.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f\n', ...
                    t(i), V(i), Dir(i), 0.0, 0.0, PLexp, 0.0, 0.0, 0.0);
            end

            fclose(fid);

            fprintf('Wrote %s\n', fname);
        end
    end
end

legend('Location', 'bestoutside');
xlim([45 80]);
hold off;

saveas(gcf, 'IEC_EOG_all_profiles.png');
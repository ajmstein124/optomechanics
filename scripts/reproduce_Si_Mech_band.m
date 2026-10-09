%% Reproduce Si snowflake mechanical band structure -- validation run
% Runs the original Si parameters from colleagues' unit_cell_3.mph.
% Single parameter point, N_ks=13 for a clean band picture.
% Goal: confirm the pipeline works and reproduce their ~7 GHz result.
%
% Run via:
%   python scripts/remote_runner.py scripts/reproduce_Si_Mech_band.m
%   (after filling in SSH credentials in remote_runner.py)
%
% Expected result: phononic bandgap near 7 GHz.

frog_folder = '';
filename = 'unit_cell_3';
model = mphload([frog_folder filename]);
save_folder = [frog_folder 'simu_data\reproduce_Si\'];
mkdir(save_folder);

%% Parameters -- original Si values, single point
scaling = 1.067;
a = 448e-9 * scaling;   % 478 nm
d = 182e-9;             % arm length
w = 99e-9;              % arm width
t = 220e-9;             % slab thickness

model.param.set('a',      num2str(a));
model.param.set('d',      num2str(d));
model.param.set('w',      num2str(w));
model.param.set('f_r',    '25e-9');
model.param.set('t',      num2str(t));

N_freqs = 10;
f0 = 7e9;
model.param.set('N_mode', num2str(N_freqs));
model.param.set('f_mech', num2str(f0));

%% BZ path: Gamma -> M -> K -> Gamma  (13 k-points per segment)
N_ks = 13;

kxs_GM = pi/a * linspace(0,   1,   N_ks);
kys_GM = pi/a * linspace(0,   1/sqrt(3), N_ks);
kxs_MK = pi/a * linspace(1,   4/3, N_ks);
kys_MK = pi/a * linspace(1/sqrt(3), 0, N_ks);
kxs_KG = pi/a * linspace(4/3, 0,   N_ks);
kys_KG = pi/a * linspace(0,   0,   N_ks);

kxs = [kxs_GM, kxs_MK(2:end), kxs_KG(2:end)];
kys = [kys_GM, kys_MK(2:end), kys_KG(2:end)];
ks  = [kxs; kys];

freqs = zeros(length(ks), 2*N_freqs);

%% Solve
for ii = 1:length(ks)
    tic
    disp(['k-point ' num2str(ii) '/' num2str(length(ks)) ...
          '  kx=' num2str(ks(1,ii),'%.3e') '  ky=' num2str(ks(2,ii),'%.3e')]);
    model.param.set('kFx', num2str(ks(1,ii)));
    model.param.set('kFy', num2str(ks(2,ii)));

    % Symmetric modes
    model.component('comp1').physics('solid').feature('as1').active(false);
    model.component('comp1').physics('solid').feature('sym1').active(true);
    model.sol('sol1').runAll;
    freqs(ii, 1:end/2) = mphglobal(model, 'solid.freq', 'Dataset', 'dset1');

    % Antisymmetric modes
    model.component('comp1').physics('solid').feature('sym1').active(false);
    model.component('comp1').physics('solid').feature('as1').active(true);
    model.sol('sol1').runAll;
    freqs(ii, end/2+1:end) = mphglobal(model, 'solid.freq', 'Dataset', 'dset1');

    % Save after each k-point so results are available for intermediate pulls
    fname_partial = [save_folder sprintf('Si_Mech_bands_nominal_ii_%d.mat', ii)];
    save(fname_partial, 'freqs', 'ks', 'a', 'd', 'w', 't', 'f0', 'N_ks');
    toc
end

%% Save final combined result
fname = [save_folder 'Si_Mech_bands_nominal.mat'];
save(fname, 'freqs', 'ks', 'a', 'd', 'w', 't', 'f0', 'N_ks');
disp(['Saved: ' fname]);

%% Plot
figure(); hold on;
for jj = 1:size(freqs, 1)
    plot(jj, 1e-9*real(freqs(jj, 1:end/2)),    'b.', 'MarkerSize', 8);
    plot(jj, 1e-9*real(freqs(jj, end/2+1:end)), 'r.', 'MarkerSize', 8);
end
ylabel('Frequency (GHz)')
xlabel('k-point')
set(gca, 'fontsize', 12)
xticks([1, N_ks, 2*N_ks-1, 3*N_ks-2]);
xticklabels({'\Gamma', 'M', 'K', '\Gamma'});
xlim([1, 3*N_ks-2])
ylim([0, 20])
legend('Symmetric', 'Antisymmetric', 'Location', 'northwest')
title('Si snowflake -- mechanical bands (reproduction)')
saveas(gcf, [save_folder 'Si_Mech_bands_nominal.jpg']);
disp('Done.');

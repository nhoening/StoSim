set terminal postscript  eps color dashed lw 6 rounded 22;
set output 'experiment2_payoff.eps';
set yrange [0:7];
set xlabel 'iteration';
set ylabel 'payoff';
set key top left spacing 1;
plot 'non-learners_in_coop/all.dat' smooth unique  title 'non-learners_in_coop' lt 1,'learners_in_coop/all.dat' smooth unique  title 'learners_in_coop' lt 2,'non-learners_in_non-coop/all.dat' smooth unique  title 'non-learners_in_non-coop' lt 3,'learners_in_non-coop/all.dat' smooth unique  title 'learners_in_non-coop' lt 4

-- VARIANTES DE AGARRE EN DOMINADAS
update ejercicios set notas_tecnicas = 'Agarre prono a la altura de los hombros, sin balanceo, barbilla sobre la barra'
  where nombre = 'Dominada estricta';
update ejercicios set notas_tecnicas = 'Agarre supino (palmas hacia ti), codos pegados, barbilla sobre la barra'
  where nombre = 'Chin-up';

insert into ejercicios (nombre, categoria, equipo, nivel, es_fijo, tipo_medida, objetivo_max, notas_tecnicas, seg_trabajo, seg_descanso) values
('Dominada agarre ancho','tiron','{barra}',3,false,'reps',6,'Manos mas anchas que los hombros, codos hacia abajo y atras',45,90),
('Dominada agarre neutro','tiron','{agarre_neutro}',2,false,'reps',8,'Palmas enfrentadas en agarres paralelos, codos pegados',45,90)
on conflict (nombre) do nothing;

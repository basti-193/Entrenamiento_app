-- SENTADILLAS PARA LAS BISERIES DE DIAS DE TIRON Y EMPUJE
insert into ejercicios (nombre, categoria, equipo, nivel, es_fijo, tipo_medida, objetivo_max, notas_tecnicas, seg_trabajo, seg_descanso) values
('Sentadilla normal','piernas','{}',1,false,'reps',15,'Talones apoyados, rodillas alineadas con los pies',40,60),
('Sentadilla con pausa abajo','piernas','{}',1,false,'reps',10,'Pausa de 2 s abajo, liviana',40,60),
('Sentadilla sumo','piernas','{}',1,false,'reps',15,'Pies abiertos, rodillas hacia afuera',40,60),
('Sentadilla isometrica','piernas','{}',1,false,'segundos',30,'Mantener la posicion a 90 grados',35,60)
on conflict (nombre) do nothing;

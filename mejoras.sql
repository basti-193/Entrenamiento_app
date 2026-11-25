-- EJERCICIOS DE TUS RUTINAS QUE FALTABAN EN EL CATALOGO
insert into ejercicios (nombre, categoria, equipo, nivel, es_fijo, tipo_medida, objetivo_max, notas_tecnicas, seg_trabajo, seg_descanso) values
('Peso muerto unilateral con mancuerna','piernas','{mancuernas}',2,false,'reps',10,'Cadera hacia atras, espalda neutra',40,60),
('Elevacion de talones a una pierna','piernas','{}',2,false,'reps',15,'Rango completo, pausa arriba',40,60),
('Y raise en TRX','hombro','{trx}',1,false,'reps',10,'Brazos en Y, escapulas abajo',35,45),
('Face pull en TRX','hombro','{trx}',1,false,'reps',12,'Codos altos, abrir el pecho',35,45),
('Curl de biceps en TRX','tiron','{trx}',1,false,'reps',12,'Codos fijos, cuerpo recto',35,60),
('Fondos entre sillas','empuje','{}',1,false,'reps',12,'Codos hacia atras, hombros abajo',35,60),
('Bear crawl','movilidad','{}',1,false,'metros',20,'Rodillas cerca del suelo, cadera baja',30,30),
('Flexion escapular','movilidad','{}',1,false,'reps',10,'Solo mover las escapulas con los brazos estirados',30,15),
('Estiramiento de isquiotibiales','movilidad','{}',1,false,'segundos',45,'Espalda larga, sin rebotes',45,15)
on conflict (nombre) do nothing;

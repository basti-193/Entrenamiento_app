-- CATALOGO AMPLIADO + TIEMPO ESTIMADO POR EJERCICIO
-- Correr en Supabase -> SQL Editor (despues del schema inicial)

alter table ejercicios add column if not exists seg_trabajo int not null default 40;
alter table ejercicios add column if not exists seg_descanso int not null default 60;

-- Ajustes de tiempo en ejercicios existentes
update ejercicios set seg_trabajo = 10, seg_descanso = 120 where nombre = 'Sprint 30 m';
update ejercicios set seg_trabajo = 15, seg_descanso = 60  where nombre = 'Salto horizontal';
update ejercicios set seg_trabajo = 12, seg_descanso = 90  where nombre = 'Dominada explosiva';
update ejercicios set seg_descanso = 90 where nombre in (
  'Dominada estricta','Dominada negativa','Dominada pecho a barra',
  'Fondo en paralelas','Sentadilla bulgara con mancuernas','Transicion muscle-up');

insert into ejercicios (nombre, categoria, equipo, nivel, es_fijo, tipo_medida, objetivo_max, notas_tecnicas, seg_trabajo, seg_descanso) values
-- Tiron y muscle-up
('Dominada con pausa arriba','tiron','{barra}',3,false,'reps',5,'Pausa de 2 s con la barbilla sobre la barra',45,90),
('Dominada arquero','tiron','{barra}',4,false,'reps',4,'Un brazo tira y el otro se extiende',45,90),
('Negativa de muscle-up','habilidad','{barra}',4,false,'reps',3,'Bajar lento pasando por la transicion',30,90),
('Muscle-up','habilidad','{barra}',6,true,'reps',3,'Tiron alto, transicion rapida y fondo',20,120),
('Fondo en barra recta','empuje','{barra}',3,false,'reps',8,'Apoyo sobre la barra con hombros adelante',35,90),
('Remo en TRX','tiron','{trx}',1,false,'reps',12,'Cuerpo recto, codos pegados al tronco',35,60),
('Remo con mancuerna a una mano','tiron','{mancuernas}',1,false,'reps',12,'Espalda neutra, sin rotar el tronco',40,60),
-- Empuje
('Flexion diamante','empuje','{}',2,false,'reps',12,'Manos juntas bajo el pecho',35,60),
('Flexion arquero','empuje','{}',3,false,'reps',6,'Un brazo flexiona y el otro queda estirado',40,60),
('Flexion pseudo planche','empuje','{}',3,false,'reps',8,'Manos junto a la cadera, hombros adelante',35,60),
('Flexion en TRX','empuje','{trx}',2,false,'reps',12,'Cuerpo en bloque, control en la bajada',35,60),
('Press militar con mancuernas','empuje','{mancuernas}',2,false,'reps',12,'Costillas abajo, sin arquear la espalda',40,60),
-- Habilidades
('Wall walk','habilidad','{}',1,false,'reps',5,'Caminar con los pies por la pared hasta el handstand',40,60),
('Handstand libre','habilidad','{}',3,true,'segundos',30,'Cuerpo en linea, controlar el balance con los dedos',30,60),
('Shoulder taps en plancha','habilidad','{}',1,false,'reps',20,'Cadera quieta al tocar el hombro',35,45),
('Planche lean','habilidad','{}',2,false,'segundos',20,'Hombros adelante de las manos, cuerpo rigido',20,60),
('Elevacion de piernas sentado','habilidad','{}',1,false,'segundos',30,'Sentado con piernas rectas, levantar los talones del suelo',20,45),
-- Core
('Elevacion de piernas colgado','core','{barra}',2,false,'reps',12,'Sin balanceo, piernas lo mas rectas posible',40,60),
('Toes to bar','core','{barra}',3,false,'reps',8,'Tocar la barra con los pies de forma controlada',40,60),
('Arch hold','core','{}',1,false,'segundos',30,'Boca abajo, levantar pecho y piernas',30,45),
('Farmer walk con mancuernas','core','{mancuernas}',1,false,'metros',40,'Postura erguida, hombros abajo',40,60),
('Kettlebell swing','piernas','{kettlebell}',2,false,'reps',15,'Bisagra de cadera, no sentadilla',35,60),
-- Piernas
('Sentadilla goblet con kettlebell','piernas','{kettlebell}',1,false,'reps',12,'Torso erguido, bajar con control',40,60),
('Pistol asistida en TRX','piernas','{trx}',2,false,'reps',6,'Usar el TRX solo para equilibrio',40,60),
('Pistol squat','piernas','{}',4,true,'reps',5,'Talon apoyado, rodilla alineada con el pie',40,90),
('Step-up con mancuernas','piernas','{mancuernas}',1,false,'reps',12,'Empujar con la pierna de arriba',40,60),
('Puente de gluteo con mancuerna','piernas','{mancuernas}',1,false,'reps',12,'Pausa arriba, costillas abajo',40,60),
('Curl femoral en TRX','piernas','{trx}',2,false,'reps',10,'Cadera alta durante todo el recorrido',35,60),
('Salto vertical','piernas','{}',2,false,'reps',5,'Aterrizaje suave, rodillas alineadas',15,60),
('Sentadilla con salto','piernas','{}',2,false,'reps',8,'Absorber el aterrizaje, sin hundir las rodillas',20,60),
-- Velocidad
('Sprint 50 m','velocidad','{cancha}',3,false,'metros',50,'Postura alta, brazos activos',8,180),
('Salida inclinada 10 m','velocidad','{cancha}',2,false,'metros',10,'Inclinacion del cuerpo y empuje potente',4,90),
('Skipping A','velocidad','{cancha}',1,false,'metros',20,'Rodilla alta, apoyo en la parte delantera del pie',15,30),
-- Movilidad
('Movilidad de tobillo en pared','movilidad','{}',1,false,'reps',10,'Rodilla hacia la pared sin levantar el talon',30,15),
('Estocada profunda (flexor de cadera)','movilidad','{}',1,false,'segundos',45,'Pelvis hacia adelante, gluteo contraido',45,15),
('Rotacion toracica','movilidad','{}',1,false,'reps',10,'Mover desde la espalda alta, cadera quieta',30,15),
('Apertura de piernas (pancake)','movilidad','{}',1,false,'segundos',60,'Espalda larga, sin forzar el rango',60,15)
on conflict (nombre) do nothing;

-- Cadenas de progresion nuevas
update ejercicios set siguiente_id = (select id from ejercicios where nombre = 'Muscle-up') where nombre = 'Transicion muscle-up';
update ejercicios set siguiente_id = (select id from ejercicios where nombre = 'Handstand en pared') where nombre = 'Wall walk';
update ejercicios set siguiente_id = (select id from ejercicios where nombre = 'Handstand libre') where nombre = 'Handstand en pared';
update ejercicios set siguiente_id = (select id from ejercicios where nombre = 'Pistol squat') where nombre = 'Pistol asistida en TRX';
update ejercicios set siguiente_id = (select id from ejercicios where nombre = 'Toes to bar') where nombre = 'Elevacion de piernas colgado';

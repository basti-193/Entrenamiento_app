-- PLANIFICADOR SEMANAL: equipo nuevo, ejercicios de gimnasio y tabla de planes
alter table ejercicios drop constraint if exists ejercicios_categoria_check;
alter table ejercicios add constraint ejercicios_categoria_check
  check (categoria in ('tiron','empuje','piernas','core','habilidad','velocidad','movilidad','hombro'));

-- Kettlebell de 4 kg es muy liviana: estos ejercicios pasan a mancuerna de 14 kg
update ejercicios set equipo = '{mancuernas}', notas_tecnicas = 'Con mancuerna de 14 kg a dos manos'
  where nombre in ('Kettlebell swing','Sentadilla goblet con kettlebell');

insert into ejercicios (nombre, categoria, equipo, nivel, es_fijo, tipo_medida, objetivo_max, notas_tecnicas, seg_trabajo, seg_descanso) values
('Jalon al pecho en maquina','tiron','{maquina}',1,false,'reps',12,'Llevar la barra al pecho, sin balancear',40,60),
('Remo sentado en maquina','tiron','{maquina}',1,false,'reps',12,'Escapulas juntas al final',40,60),
('Curl de biceps con mancuernas','tiron','{mancuernas}',1,false,'reps',12,'Codos pegados, bajada lenta',35,60),
('Curl de biceps con banda','tiron','{bandas}',1,false,'reps',15,'Tension constante',35,45),
('Press de pecho en maquina','empuje','{maquina}',1,false,'reps',12,'Hombros atras y abajo',40,60),
('Press en suelo con mancuernas','empuje','{mancuernas}',1,false,'reps',12,'Codos a 45 grados del tronco',40,60),
('Aperturas con banda','empuje','{bandas}',1,false,'reps',15,'Brazos casi estirados, apretar el pecho',35,45),
('Extension de triceps en polea','empuje','{maquina}',1,false,'reps',12,'Codos fijos al costado',35,60),
('Press de hombros en maquina','hombro','{maquina}',1,false,'reps',12,'Sin arquear la espalda',40,60),
('Elevaciones laterales con mancuernas','hombro','{mancuernas}',1,false,'reps',15,'Subir hasta la altura del hombro',35,45),
('Face pull con banda','hombro','{bandas}',1,false,'reps',15,'Codos altos, abrir hacia afuera',35,45),
('Pajaros con mancuernas','hombro','{mancuernas}',1,false,'reps',15,'Torso inclinado, espalda neutra',35,45),
('Rueda abdominal','core','{rueda}',2,false,'reps',10,'Desde las rodillas, sin hundir la zona lumbar',30,60),
('Crunch en polea','core','{maquina}',1,false,'reps',15,'Enrollar el tronco, no tirar con los brazos',35,45),
('Pallof press con banda','core','{bandas}',1,false,'reps',12,'Resistir la rotacion',35,45),
('Extension de cuadriceps en maquina','piernas','{maquina}',1,false,'reps',15,'Pausa arriba',40,60),
('Salto al cajon bajo','piernas','{cajon}',2,false,'reps',6,'Cajon de 20 cm, bajar caminando',15,60)
on conflict (nombre) do nothing;

create table if not exists planes (
  semana_inicio date primary key,
  dias jsonb,
  texto text not null,
  creado timestamptz default now()
);
grant all on planes to service_role;

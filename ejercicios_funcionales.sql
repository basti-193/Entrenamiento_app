-- LISTADO FUNCIONAL: tren inferior, locomocion, empuje, tiron, core, movilidad, potencia, habilidades y velocidad estatica
alter table ejercicios drop constraint if exists ejercicios_categoria_check;
alter table ejercicios add constraint ejercicios_categoria_check
  check (categoria in ('tiron','empuje','piernas','core','habilidad','velocidad','movilidad','hombro','locomocion'));

insert into ejercicios (nombre, categoria, equipo, nivel, es_fijo, tipo_medida, objetivo_max, notas_tecnicas, seg_trabajo, seg_descanso) values
-- Cuadriceps y rodillas
('Sissy squat','piernas','{}',3,false,'reps',10,'Rodillas adelante, torso inclinado hacia atras, con apoyo si hace falta',40,60),
('Curl nordico inverso','piernas','{}',2,false,'reps',8,'De rodillas, inclinar el torso hacia atras con control',40,60),
('ATG split squat','piernas','{}',2,false,'reps',10,'Rodilla adelante sobre el pie, rango completo',40,60),
('Shrimp squat','piernas','{}',4,false,'reps',5,'Pie trasero tomado, bajar la rodilla al suelo con control',40,90),
('Step down con cajon','piernas','{cajon}',1,false,'reps',12,'Bajar lento con una pierna, rodilla alineada',40,60),
('Skater squat','piernas','{}',3,false,'reps',8,'Bajar a una pierna con el otro pie atras',40,60),
('Hindu squat','piernas','{}',2,false,'reps',15,'Brazos en arco, ritmo fluido, talones se elevan',40,60),
('Sentadilla en pared (wall sit)','piernas','{}',1,false,'segundos',45,'Espalda a la pared, muslos a 90 grados',45,60),
-- Isquiotibiales y gluteos
('Nordic curl','piernas','{ancla}',4,false,'reps',5,'Bajar el torso con control, pies bien enganchados',40,90),
('Puente de gluteo a una pierna','piernas','{}',1,false,'reps',12,'Pausa arriba, cadera nivelada',40,60),
('Peso muerto rumano a una pierna','piernas','{}',2,false,'reps',10,'Bisagra de cadera, espalda neutra',40,60),
('Curl femoral deslizante','piernas','{}',2,false,'reps',10,'Talones sobre una toalla en piso liso, cadera arriba',35,60),
('Hip thrust a una pierna','piernas','{cajon}',2,false,'reps',10,'Espalda alta apoyada en el cajon, pausa arriba',40,60),
('Buenos dias','piernas','{}',1,false,'reps',12,'Manos tras la cabeza, bisagra con espalda neutra',35,60),
('Bisagra de cadera a una pierna','piernas','{}',1,false,'reps',10,'Pierna atras como contrapeso, cadera cuadrada',35,60),
('Caminata de isquios (walkouts)','piernas','{}',2,false,'reps',8,'Desde el puente, caminar los talones hacia afuera',35,60),
-- Potencia
('Salto tuck','piernas','{}',3,false,'reps',6,'Rodillas al pecho en el aire, aterrizaje suave',15,60),
('Salto skater (lateral)','piernas','{}',2,false,'reps',10,'Salto lateral a una pierna, aterrizaje controlado',20,60),
('Salto en split squat','piernas','{}',3,false,'reps',8,'Alternar piernas en el aire, aterrizaje suave',20,60),
('Salto pogo','piernas','{}',1,false,'reps',20,'Rebotes cortos con tobillos rigidos',20,45),
('Flexion explosiva','empuje','{}',3,false,'reps',6,'Empujar hasta despegar las manos',20,60),
('Flexion con palmada','empuje','{}',4,false,'reps',5,'Despegar y aplaudir, aterrizar con codos suaves',20,90),
-- Empuje
('Flexion hindu','empuje','{}',3,false,'reps',8,'Cadera arriba y pecho hacia adelante en un solo flujo',40,60),
('Flexion typewriter','empuje','{}',4,false,'reps',6,'Desplazarse de lado a lado con los brazos extendidos',40,60),
('Press de pecho en TRX','empuje','{trx}',2,false,'reps',12,'Cuerpo en bloque, codos a 45 grados',35,60),
('Extension de triceps en TRX','empuje','{trx}',2,false,'reps',12,'Codos fijos, cuerpo recto',35,60),
('Flexion en pino (handstand push-up)','empuje','{pared}',5,false,'reps',5,'En pared, bajar la cabeza con control',40,90),
-- Tiron
('Dominada typewriter','tiron','{barra}',5,false,'reps',4,'Desplazarse de lado a lado arriba de la barra',40,90),
('Dominada commando','tiron','{barra}',4,false,'reps',5,'Agarre lateral, cabeza alternando lados',40,90),
('T raise en TRX','hombro','{trx}',1,false,'reps',10,'Brazos en T, escapulas juntas',35,45),
-- Core
('Plancha lateral estrella','core','{}',3,false,'segundos',20,'Brazo y pierna arriba en plancha lateral',25,45),
('Bird dog','core','{}',1,false,'reps',10,'Brazo y pierna opuestos, cadera quieta',35,45),
('Body saw','core','{}',3,false,'reps',10,'Plancha balanceando adelante y atras, con toalla o deslizadores',35,60),
('Turkish get-up','core','{kettlebell}',2,false,'reps',5,'Lento y controlado, con la kettlebell de 4 kg',45,60),
('Bear plank','core','{}',1,false,'segundos',30,'Rodillas cerca del suelo, espalda plana',30,45),
('Elevacion de rodillas colgado','core','{barra}',1,false,'reps',12,'Sin balanceo',40,60),
('Dragon flag','core','{ancla}',5,false,'reps',4,'Cuerpo rigido, bajar con control',30,90),
('Limpiaparabrisas colgado','core','{barra}',5,false,'reps',6,'Piernas rectas, rotar desde el tronco',40,90),
-- Movilidad activa y fuerza articular
('Jefferson curl','movilidad','{}',3,false,'reps',8,'Sin carga, bajar vertebra a vertebra con piernas rectas',40,30),
('Pancake good morning','movilidad','{}',2,false,'reps',10,'Piernas abiertas, bisagra con espalda larga',40,30),
('Shoulder CARs','movilidad','{}',1,false,'reps',5,'Circulos lentos al maximo rango, por lado',40,15),
('Hip CARs','movilidad','{}',1,false,'reps',5,'Circulos lentos de cadera, por lado',40,15),
('Ankle CARs','movilidad','{}',1,false,'reps',10,'Circulos amplios de tobillo, por lado',30,15),
('90/90 hip switches','movilidad','{}',1,false,'reps',8,'Rotar las rodillas de un lado a otro sin usar las manos',40,15),
('Cossack hold','movilidad','{}',1,false,'segundos',30,'Posicion lateral profunda, talon apoyado',30,15),
('Wrist push-ups (muneca)','movilidad','{}',1,false,'reps',10,'Cargar peso en la muneca de forma progresiva, sin dolor',30,15),
('Elevacion de tibial (tibialis raise)','movilidad','{}',1,false,'reps',15,'Espalda a la pared, subir la punta de los pies',30,30),
('German hang','movilidad','{barra}',5,false,'segundos',15,'Progresion gradual, hombros activos, sin dolor',20,60),
('Skin the cat','movilidad','{barra}',5,false,'reps',3,'Progresion gradual y controlada',30,60),
('Puente (progresion)','movilidad','{}',3,false,'segundos',20,'Empujar con piernas y hombros, sin dolor lumbar',30,30),
-- Equilibrio y habilidades
('Crow pose','habilidad','{}',2,false,'segundos',20,'Rodillas sobre los triceps, mirada adelante',20,45),
('Frog stand','habilidad','{}',1,false,'segundos',20,'Rodillas sobre los codos, inclinar el peso adelante',20,45),
('Elbow lever','habilidad','{}',4,false,'segundos',10,'Cuerpo rigido sobre los codos',15,60),
('L-sit a tuck planche','habilidad','{paralelas}',5,false,'reps',3,'Transicion lenta con hombros adelante',25,90),
('Equilibrio a una pierna','habilidad','{}',1,false,'segundos',30,'Mirada fija, cadera nivelada',30,30),
('Pistol squat isometrico','habilidad','{}',4,false,'segundos',10,'Mantener abajo con el talon apoyado',15,60),
-- Locomocion
('Ape walk','locomocion','{}',1,false,'segundos',30,'Sentadilla profunda, mover manos y pies de forma alternada',30,30),
('Monkey walk','locomocion','{}',2,false,'segundos',30,'Caminar con el cuerpo bajo y las caderas altas',30,30),
('Crab walk','locomocion','{}',1,false,'segundos',30,'Pelvis arriba, avanzar con manos y pies',30,30),
('Lateral bear crawl','locomocion','{}',1,false,'segundos',30,'Rodillas bajas, desplazarse de lado',30,30),
('Duck walk','locomocion','{}',1,false,'segundos',30,'Sentadilla profunda, caminar manteniendo la altura',30,30),
('Beast reach','locomocion','{}',2,false,'segundos',30,'Desde la posicion de bestia, estirar un brazo al frente',30,30),
('Leopard crawl','locomocion','{}',2,false,'segundos',30,'Cuerpo pegado al suelo, avanzar con brazos y piernas',30,30),
('Inchworm','locomocion','{}',1,false,'segundos',30,'Caminar con las manos hasta la plancha y volver',30,30),
('Spiderman crawl','locomocion','{}',2,false,'segundos',30,'Llevar la rodilla al codo del mismo lado al avanzar',30,30),
('Ground flow','locomocion','{}',2,false,'segundos',30,'Encadenar posiciones en el suelo con fluidez',30,30),
('Sit through','locomocion','{}',2,false,'segundos',30,'Desde la plancha, pasar una pierna por debajo del cuerpo',30,30),
('Kick through','locomocion','{}',2,false,'segundos',30,'Desde cuadrupedia, pasar la pierna por delante con rotacion',30,30),
('Underswitch','locomocion','{}',3,false,'segundos',30,'Cambio de piernas por debajo con las manos apoyadas',30,30),
('Beast to crab','locomocion','{}',2,false,'segundos',30,'Transicion de cuadrupedia a cangrejo con rotacion',30,30),
-- Velocidad estatica para casa (sin espacio)
('Piques en el lugar','velocidad','{}',2,false,'segundos',30,'Maxima frecuencia de pies, brazos activos',30,60),
('Rodillas altas en el lugar','velocidad','{}',1,false,'segundos',30,'Rodillas a la altura de la cadera, ritmo rapido',30,60),
('Talones al gluteo en el lugar','velocidad','{}',1,false,'segundos',30,'Talones al gluteo, torso erguido',30,60),
('Skipping en el lugar','velocidad','{}',1,false,'segundos',30,'Skipping A, apoyo en la parte delantera del pie',30,60)
on conflict (nombre) do nothing;

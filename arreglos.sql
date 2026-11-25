-- El remo invertido exigia barra Y TRX a la vez; basta con una barra baja
update ejercicios set equipo = '{barra}', notas_tecnicas = 'Cuerpo recto bajo una barra baja, escapulas juntas'
  where nombre = 'Remo invertido';

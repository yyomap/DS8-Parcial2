-- Consultas del histórico (las mismas que usa consultas.py).
-- Los timestamps son Unix en UTC; hora_sincronizada = 1 descarta lecturas con fecha falsa (año 2000).

-- 1. Lecturas entre dos momentos (cambia los dos números por timestamps Unix)
SELECT timestamp, movimiento, distancia, alarma, armado
FROM lecturas
WHERE timestamp BETWEEN 1762000000 AND 1762100000 AND hora_sincronizada = 1
ORDER BY timestamp;

-- 2. Eventos de un tipo (ALARMA_ACTIVADA, COMANDO_RECHAZADO, COMANDO_EJECUTADO, ...)
SELECT timestamp, detalle
FROM eventos
WHERE tipo = 'ALARMA_ACTIVADA' AND hora_sincronizada = 1
ORDER BY timestamp;

-- 3. Cuántas veces se activó la alarma
SELECT COUNT(*)
FROM eventos
WHERE tipo = 'ALARMA_ACTIVADA' AND hora_sincronizada = 1;

-- 4. Resumen de eventos por tipo
SELECT tipo, COUNT(*)
FROM eventos
WHERE hora_sincronizada = 1
GROUP BY tipo
ORDER BY COUNT(*) DESC;

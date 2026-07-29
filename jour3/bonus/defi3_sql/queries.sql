-- Défi 3 - Analyse SQL sur bourse.db (palmarès Boursorama)

-- Top 5 hausses et baisses du jour
SELECT libelle, variation, cours
FROM actions
ORDER BY variation DESC LIMIT 5;

SELECT libelle, variation, cours
FROM actions
ORDER BY variation ASC LIMIT 5;

-- Actions avec volume anormalement élevé (> 2x la médiane)
SELECT libelle, volume, cours
FROM actions
WHERE volume > (
    SELECT AVG(volume) * 2 FROM actions
)
ORDER BY volume DESC;

-- Exporter le résultat en CSV directement depuis SQLite
.mode csv
.output analyse_bourse.csv
SELECT * FROM actions ORDER BY variation DESC;
.output stdout

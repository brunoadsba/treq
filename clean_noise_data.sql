-- Limpeza de ruído nos dados existentes
-- Remove checkboxes vazios e prefixos de fonte

UPDATE knowledge_base 
SET document = regexp_replace(document, '\[Fonte:.*?\|.*?\]', '', 'g')
WHERE document ~ '\[Fonte:.*?\|.*?\]';

UPDATE knowledge_base 
SET document = regexp_replace(document, '^\s*-\s*\[\s*\]\s*', '', 'gm')
WHERE document ~ '^\s*-\s*\[\s*\]\s*';

UPDATE knowledge_base 
SET document = regexp_replace(document, '\*\*([^*]+)\*\*:?\s*$', '', 'gm')
WHERE document ~ '\*\*([^*]+)\*\*:?\s*$';

UPDATE knowledge_base 
SET document = regexp_replace(document, '\|\s*Parte:\s*\d+/\d+\s*\]', '', 'g')
WHERE document ~ '\|\s*Parte:\s*\d+/\d+\s*\]';

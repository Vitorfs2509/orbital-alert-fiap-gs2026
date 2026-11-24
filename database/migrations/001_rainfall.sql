-- Run inside a transaction. The previous project schema used PostgreSQL's
-- default constraint name sensors_type_check for the column-level CHECK.
LOCK TABLE sensors IN ACCESS EXCLUSIVE MODE;
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'sensors'::regclass AND conname = 'sensors_type_check'
          AND strpos(pg_get_constraintdef(oid), '''RAINFALL''') > 0
    ) THEN
        RETURN;
    END IF;

    ALTER TABLE sensors DROP CONSTRAINT IF EXISTS sensors_type_check;
    UPDATE sensors SET type = 'RAINFALL' WHERE type = 'RAIN';
    ALTER TABLE sensors ADD CONSTRAINT sensors_type_check
        CHECK (type IN ('RAINFALL', 'TEMPERATURE', 'HUMIDITY', 'WATER_LEVEL', 'SMOKE'));
END $$;

-- upgrade --
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
ALTER TABLE "bot" ADD "code" UUID NOT NULL DEFAULT uuid_generate_v4();
-- downgrade --
ALTER TABLE "bot" DROP COLUMN "code";

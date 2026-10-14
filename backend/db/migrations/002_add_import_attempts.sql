ALTER TABLE image_imports ADD COLUMN attempt_token TEXT;
ALTER TABLE image_imports ADD COLUMN extracted_payload TEXT;
ALTER TABLE image_imports ADD COLUMN publication_digest TEXT;

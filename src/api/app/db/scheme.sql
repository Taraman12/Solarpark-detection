CREATE TABLE "solarpark" (
  "solarpark_id" int PRIMARY KEY,
  "size_in_sq_m" float4,
  "peak_power" float4,
  "first_detected" date,
  "last_detected" date,
  "avg_confidence" float,
  "is_valid" str,
  "comment" str,
  "lat" List[int],
  "lon" List[int],
  "geom" geography(POLYGON,4267)
);

CREATE TABLE "prediction" (
  "id" int PRIMARY KEY,
  "solarpark_id" int,
  "date_of_data" date,
  "size_in_sq_m" float,
  "peak_power" float,
  "avg_confidence" float,
  "comment" str,
  "lat" List[int],
  "lon" List[int],
  "geom" geography(POLYGON,4267)
);

CREATE TABLE "aws_instance" (
  "id" int PRIMARY KEY,
  "status" str,
  "service" str,
  "ec2_instance_id" str
);

ALTER TABLE "solarpark" ADD FOREIGN KEY ("solarpark_id") REFERENCES "prediction" ("solarpark_id");

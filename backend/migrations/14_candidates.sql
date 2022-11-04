

CREATE TYPE candidate_type as ENUM(
    'house',
    'bus_station',
    'culture_house',
    'library',
    'metro',
    'mfc',
    'nto_non_paper',
    'nto_paper',
    'parking',
    'postamat',
    'sports',
    'any'
);


CREATE TABLE candidates(
    id SERIAL PRIMARY KEY,
    abbrev_ao VARCHAR(7) NOT NULL,
    district_id INTEGER NOT NULL,
    point GEOMETRY(POINT) NOT NULL,
    address VARCHAR,
    type candidate_type NOT NULL DEFAULT candidate_type('any'),

    calculated_radius FLOAT NOT NULL,
    state_modifier FLOAT NOT NULL,
    district_modifier FLOAT NOT NULL,

    metro_count INT NOT NULL,
    metro_min_dest FLOAT NOT NULL,
    metro_nearest_modifier FLOAT NOT NULL,
    metro_average_dest FLOAT NOT NULL,
    metro_average_modifier FLOAT NOT NULL,

    postamats_count INT NOT NULL,
    postamats_min_dest FLOAT NOT NULL,
    postamats_nearest_modifier FLOAT NOT NULL,
    postamats_average_dest FLOAT NOT NULL,
    postamats_average_modifier FLOAT NOT NULL,

    parkings_count INT NOT NULL,
    parkings_min_dest FLOAT NOT NULL,
    parkings_nearest_modifier FLOAT NOT NULL,
    parkings_average_dest FLOAT NOT NULL,
    parkings_average_modifier FLOAT NOT NULL,

    bus_stations_count INT NOT NULL,
    bus_stations_min_dest FLOAT NOT NULL,
    bus_stations_nearest_modifier FLOAT NOT NULL,
    bus_stations_average_dest FLOAT NOT NULL,
    bus_stations_average_modifier FLOAT NOT NULL,

    culture_houses_count INT NOT NULL,
    culture_houses_min_dest FLOAT NOT NULL,
    culture_houses_average_dest FLOAT NOT NULL,

    libraries_count INT NOT NULL,
    libraries_min_dest FLOAT NOT NULL,
    libraries_nearest_modifier FLOAT NOT NULL,
    libraries_average_dest FLOAT NOT NULL,
    libraries_average_modifier FLOAT NOT NULL,

    mfc_count INT NOT NULL,
    mfc_min_dest FLOAT NOT NULL,
    mfc_nearest_modifier FLOAT NOT NULL,
    mfc_average_dest FLOAT NOT NULL,
    mfc_average_modifier FLOAT NOT NULL,

    sports_count INT NOT NULL,
    sports_min_dest FLOAT NOT NULL,
    sports_nearest_modifier FLOAT NOT NULL,
    sports_average_dest FLOAT NOT NULL,
    sports_average_modifier FLOAT NOT NULL,

    nto_paper_count INT NOT NULL,
    nto_paper_min_dest FLOAT NOT NULL,
    nto_paper_average_dest FLOAT NOT NULL,

    nto_non_paper_count INT NOT NULL,
    nto_non_paper_min_dest FLOAT NOT NULL,
    nto_non_paper_average_dest FLOAT NOT NULL,

    houses_count INT NOT NULL,
    houses_min_dest FLOAT NOT NULL,
    houses_nearest_modifier FLOAT NOT NULL,
    houses_average_dest FLOAT NOT NULL,
    houses_average_modifier FLOAT NOT NULL,

    modifier_v1 FLOAT NOT NULL,
    modifier_v2 FLOAT NOT NULL,

    CONSTRAINT fk_abbrev_ao FOREIGN KEY(abbrev_ao) REFERENCES states(abbrev),
    CONSTRAINT fk_district_id FOREIGN KEY(district_id) REFERENCES districts(id)
);

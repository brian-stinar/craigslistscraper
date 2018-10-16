DROP TABLE IF EXISTS states;
CREATE TABLE states(
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    stateName VARCHAR(15),
    stateUrl VARCHAR(2083), # https://stackoverflow.com/questions/219569/best-database-field-type-for-a-url
    dateCreated TIMESTAMP,
    deleted int # Problems with TIMESTAMP here...? 
);

DROP TABLE IF EXISTS cities;
CREATE TABLE cities(
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    cityName VARCHAR(50),
    cityUrl VARCHAR(2083), 
    dateCreated TIMESTAMP, 
    deleted int
);

CREATE TABLE test.covid_data(
    id int primary key auto_increment,
    province_state varchar(256),
    country_region varchar(256),
    lat float,
    lon float,
    date datetime,
    confirmed int,
    deaths int,
    recovered int
);
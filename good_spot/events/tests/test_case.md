* There are 3 cities in different timezones: 
Kyiv +2/+3 'Europe/Kiev'
Quito -5 'America/Guayaquil'
Tokyo +9 'Asia/Tokyo'

* There are place type Bar available in all cities

* There are 10 places:
2 places in Kyiv
3 places in Quito
5 places in Tokyo

* There are rules for updating bars:
Rule contains time in UTC but should be ran at local time,
e.g. there is rule with time 11AM, it means rul should be started at 11AM of local time of each city.

1) Update bars at 18:00
2) Update bars at 21:00

==== Case 1 =====:
- There is xx:xx (15:00) utc server time
- Check current time in all cities:
--- Kyiv xx:xx+3 (18:00) tz='Europe/Kiev'
--- Find the rule with time xx:xx+3 (18:00) tz=UTC
--- There is one rule
--- Run updating for places with type Bar in city Kyiv
--- 2 places should be updated


--- Quito xx:xx-5 (10:00) tz='America/Guayaquil'
--- Find the rule with time xx:xx-5 (10:00) tz=UTC
--- There are no rules


--- Tokyo xx:xx+9 (00:00) tz='Asia/Tokyo'
--- Find the rule with time xx:xx+9 (00:00) tz=UTC
--- There are no rules


==== Case 2 =====:
- There is xx:xx (09:00) utc server time
- Check current time in all cities:
--- Kyiv xx:xx+3 (12:00) tz='Europe/Kiev'
--- Find the rule with time xx:xx+3 (12:00) tz=UTC
--- There are no rules


--- Quito xx:xx-5 (04:00) tz='America/Guayaquil'
--- Find the rule with time xx:xx-5 (04:00) tz=UTC
--- There are no rules


--- Tokyo xx:xx+9 (18:00) tz='Asia/Tokyo'
--- Find the rule with time xx:xx+9 (18:00) tz=UTC
--- There is one rule
--- Run updating for places with type Bar in city Tokyo
--- 5 places should be updated



from operator import itemgetter

import requests
import numpy as np

API_URI = 'https://api.nasa.gov/neo/rest/v1/neo/browse?api_key={key}&page={page}'
settings = {
    'page': 0,
    'key': 'DEMO_KEY'  # get API_KEY here - https://api.nasa.gov/index.html#apply-for-an-api-key
}
data = {}


def handle_asteroids_data():
    '''Generate asteroids dict.'''

    asteroids = {}
    r = requests.get(API_URI.format(**settings))
    # return code validation skipped
    payload = r.json()
    for obj in payload['near_earth_objects']:
        estimated_diameter = [
            obj['estimated_diameter']['kilometers']['estimated_diameter_min'],
            obj['estimated_diameter']['kilometers']['estimated_diameter_max']]

        if not obj.get('close_approach_data', []):
            speed = 0
        else:
            speed = []
            for approach in obj['close_approach_data']:
                speed.append(float(approach['relative_velocity']['kilometers_per_hour']))

        avg_diameter = np.mean(estimated_diameter)
        asteroids[obj['name']] = {
            'name': obj['name'], 'is_hazardous': obj['is_potentially_hazardous_asteroid'],
            'avg_diameter': avg_diameter, 'id': obj['neo_reference_id'],
            'avg_speed': np.mean(speed)
        }
    return asteroids

for _ in xrange(15):  # first 15-th pages
    # API rate limit for DEMO KEY + IP is ~30 req/h.. oh and ~50 req/day
    asteroids = handle_asteroids_data()
    data.update(asteroids)
    settings['page'] += 1

# change data structure for now
neo = [(v['id'], v['name'], v['avg_diameter'], v['avg_speed'], v['is_hazardous']) for _, v in data.iteritems()]

top_biggest = sorted(neo, key=lambda obj: obj[2], reverse=True)[:5]
top_fastest = sorted(neo, key=lambda obj: obj[3], reverse=True)[:5]
# sort by (4,2,3) - is_hazardous(first), diameter, speed
top_dangerous = sorted(neo, key=itemgetter(4, 2, 3), reverse=True)[:5]

print 'Top biggest asteroids:'
template = "{0:10}{1:20}{2:12}"
print template.format("ID", "NAME", "DIAMETER(avg)")
for entry in top_biggest:
    print template.format(*entry)

print 'Top fastest asteroids:'
template = "{0:10}{1:20}{3:12}"
print template.format("ID", "NAME", "", "SPEED(avg)")
for entry in top_fastest:
    print template.format(*entry)

print 'Most dangerous asteroids:'
template = "{0:10}{1:20}{2:20}{3:20}"
print template.format("ID", "NAME", "DIAMETER(avg km)", "SPEED(avg km/h)")
for entry in top_dangerous:
    print template.format(*entry)

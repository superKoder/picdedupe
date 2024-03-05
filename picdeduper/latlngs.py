
import math
import re

from typing import Dict

from picdeduper import jsonable

Degrees = float
DistanceInKm = float

RE_LATLNG = re.compile(r"<([\+\-]?\d+\.?\d*),([\+\-]?\d+\.?\d*)>")


class LatLng(jsonable.Jsonable):
    """Represents at latitude-longitude, an optionally an altitude"""

    def __init__(self, latitude: Degrees, longitude: Degrees, altitude: Degrees = 0.) -> None:
        self.latitude = latitude
        assert (self.latitude <= +180. and self.latitude >= -180.)
        self.longitude = longitude
        assert (self.longitude <= +180. and self.longitude >= -180.)
        self.altitude = altitude

    def distance_in_degrees(self, other: object) -> Degrees:
        """
        WARNING: 
        Measuring distance in degrees is not smart, because the 
        thresholds would be bigger on the equator that on the poles.
        """
        assert isinstance(other, LatLng)
        lat_diff = abs(self.latitude - other.latitude)
        lng_diff = abs(self.longitude - other.longitude)
        return math.sqrt(lat_diff ** 2 + lng_diff ** 2)

    def distance_in_km(self, other: object, decimals=3) -> DistanceInKm:
        assert isinstance(other, LatLng)
        EARTH_RADIUS: DistanceInKm = 6378.137
        dLat = other.latitude * math.pi / 180 - self.latitude * math.pi / 180
        dLon = other.longitude * math.pi / 180 - self.longitude * math.pi / 180
        a = (
            math.sin(dLat/2) * math.sin(dLat/2) +
            math.cos(self.latitude * math.pi / 180) * math.cos(other.latitude * math.pi / 180) *
            math.sin(dLon/2) * math.sin(dLon/2)
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        km = EARTH_RADIUS * c
        return round(km, decimals)

    def as_string(self) -> str:
        if not self.latitude or not self.longitude:
            return None
        # TODO: altitude?
        return f"<{self.latitude},{self.longitude}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LatLng):
            return False
        if not math.isclose(self.latitude, other.latitude,):
            return False
        if not math.isclose(self.longitude, other.longitude):
            return False
        if not math.isclose(self.altitude, other.altitude):
            return False
        return True

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(object)

    def __str__(self) -> str:
        return self.as_string()

    def __repr__(self) -> str:
        return f"LatLng({self.latitude}, {self.longitude}, {self.altitude})"

    def as_jsonable(self) -> Dict:
        return {
            "lat": jsonable.to(self.latitude),
            "lng": jsonable.to(self.longitude),
        }


def parse_latlng(string: str) -> LatLng:
    """Parses a <lat,lng> string into a LatLng object"""
    if not string: return None
    matches = RE_LATLNG.match(string)
    if matches:
        return LatLng(
            latitude=float(matches.group(1)),
            longitude=float(matches.group(2)),
        )


# Test data
SAN_JOSE = LatLng(37.335480, -121.893028)
SAN_FRANCISCO = LatLng(37.773972, -122.431297)
NEW_YORK = LatLng(40.776676, -73.971321)
LONDON = LatLng(51.509865, -0.118092)
PARIS = LatLng(48.864716, 2.349014)
BRUSSELS = LatLng(50.85045, 4.34878)

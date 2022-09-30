from django.http import JsonResponse
import json
from .acls import get_photo, get_weather_data

from .models import Conference, Location, State
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods


class ConferenceListEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
    ]


def api_list_conferences(request):
    if request.method == "GET":
        conferences = Conference.objects.all()
        return JsonResponse(
            {"conferences": conferences},
            encoder=ConferenceListEncoder,
        )
    else:
        content = json.loads(request.body)

        # Get the Location object and put it in the content dict
        try:
            location = Location.objects.get(id=content["location"])
            content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid location id"},
                status=400,
            )

        conference = Conference.objects.create(**content)
        return JsonResponse(
            conference,
            encoder=ConferenceDetailEncoder,
            safe=False,
        )


class LocationListEncoder(ModelEncoder):
    model = Location
    properties = ["name"]


class LocationDetailEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
        "city",
        "room_count",
        "created",
        "updated",
        "picture_url",
    ]

    def get_extra_data(self, o):
        return {"state": o.state.abbreviation}


class ConferenceDetailEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
        "description",
        "max_presentations",
        "max_attendees",
        "starts",
        "ends",
        "created",
        "updated",
        "location",
    ]
    encoders = {
        "location": LocationListEncoder(),
    }


def api_show_conference(request, pk):
    conference = Conference.objects.get(id=pk)
    state_abv = conference.location.state
    city_name = conference.location.city
    print(city_name)
    return JsonResponse(
        {
            "conference": conference,
            "weather": get_weather_data(city_name, state_abv),
        },
        encoder=ConferenceDetailEncoder,
        safe=False,
    )
    # conference = Conference.objects.get(id=pk)
    # return JsonResponse(
    #     {
    #         "name": conference.name,
    #         "starts": conference.starts,
    #         "ends": conference.ends,
    #         "description": conference.description,
    #         "created": conference.created,
    #         "updated": conference.updated,
    #         "max_presentations": conference.max_presentations,
    #         "max_attendees": conference.max_attendees,
    #         "location": {
    #             "name": conference.location.name,
    #             "href": conference.location.get_api_url(),
    #         },
    #     }
    # )


@require_http_methods(["GET", "POST"])
def api_list_locations(request):
    if request.method == "GET":
        locations = Location.objects.all()
        return JsonResponse(
            {"locations": locations},
            encoder=LocationListEncoder,
        )
    else:
        content = json.loads(request.body)

        # Get the State object and put it in the content dict
        try:
            state = State.objects.get(abbreviation=content["state"])
            content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
            )
        photo = get_photo(content["city"], content["state"].abbreviation)
        content.update(photo)
        location = Location.objects.create(**content)
        return JsonResponse(location, encoder=LocationListEncoder, safe=False)


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_location(request, pk):
    """
    Returns the details for the Location model specified
    by the pk parameter.

    This should return a dictionary with the name, city,
    room count, created, updated, and state abbreviation.

    {
        "name": location's name,
        "city": location's city,
        "room_count": the number of rooms available,
        "created": the date/time when the record was created,
        "updated": the date/time when the record was updated,
        "state": the two-letter abbreviation for the state,
    }
    """
    if request.method == "GET":
        location = Location.objects.get(id=pk)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Location.objects.filter(id=pk).delete()
        return JsonResponse({"deleted": count > 0})

    else:
        # copied from create
        content = json.loads(request.body)
        try:
            # new code
            if "state" in content:
                state = State.objects.get(abbreviation=content["state"])
                content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
            )

        # new code
        Location.objects.filter(id=pk).update(**content)

        # copied from get detail
        location = Location.objects.get(id=pk)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )
    # location = Location.objects.get(id=pk)
    # print("location here", location.city)
    # return JsonResponse(
    #     {
    #         "name": location.name,
    #         "city": location.city,
    #         "room_count": location.room_count,
    #         "created": location.created,
    #         "updated": location.updated,
    #         "state": location.state.abbreviation,
    #     }
    # )

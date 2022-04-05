from rest_framework import serializers
from .models import Car


class CarSerializer(serializers.ModelSerializer):
    prices = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Car
        fields = ["automaker", "model", "year", "type", "is_available", "price", "prices"]

    @staticmethod
    def get_prices(obj):
        day = obj.price
        month = day * 30  # 30 days
        three_months = month * 3  # 90 days
        six_months = month * 6  # 180 days
        year = day * 365  # 365 days
        vat = 0.77  # 23%
        prices = {
            "brutto":
                {
                    "day": day,
                    "month": month,
                    "threeMonths": three_months,
                    "sixMonths": six_months,
                    "year": year
                },
            "netto":
                {
                    "day": round(float(day) * vat, 2),
                    "month": round(float(month) * vat, 2),
                    "threeMonths": round(float(three_months) * vat, 2),
                    "sixMonths": round(float(six_months) * vat, 2),
                    "year": round(float(year) * vat, 2),
                }
        }
        return prices

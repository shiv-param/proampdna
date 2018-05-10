from rest_framework import serializers
import application.models as app_models


class SpecieSerializer(serializers.ModelSerializer):

    specie_data = serializers.SerializerMethodField()

    def get_specie_data(self, obj):
        return list(map(lambda each_data: {
            'triplet': each_data.triplet,
            'amino_acid': each_data.amino_acid,
            'fraction': each_data.fraction,
            'frequency': each_data.frequency
        }, app_models.SpecieData.objects.filter(specie=obj)))

    def create(self, validated_data):
        (specie_obj, created) = app_models.Specie.objects.get_or_create(**validated_data)
        return specie_obj

    class Meta:
        model = app_models.Specie
        fields = ("specie_id", "specie_head", "specie_data")


class ResultSet(object):
    def __init__(self, **kwargs):
        for field in ('GCPerc', 'forwardPrimer', 'meltingPoint', 'length', 'frequency', 'reversePrimer'):
            setattr(self, field, kwargs.get(field, None))


class ResultSetSerializer(serializers.Serializer):
    GCPerc = serializers.IntegerField()
    forwardPrimer = serializers.CharField(max_length=256)
    meltingPoint = serializers.FloatField()
    length = serializers.IntegerField()
    frequency = serializers.FloatField()
    reversePrimer = serializers.CharField(max_length=256)
    aasldc = serializers.CharField(max_length=256)

    def create(self, validated_data):
        return ResultSet(**validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        return instance
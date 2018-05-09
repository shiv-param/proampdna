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
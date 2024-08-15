from django.contrib.auth.models import Group, User
from rest_framework import serializers

from orders.models import Order


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        # fields = ['id', 'order_number', 'delivery_date', 'receiving_company_name']
        fields = serializers.ALL_FIELDS
        extra_kwargs = {'receiving_company_id': {'write_only': True},
                        'additional_notes': {'write_only': True},
                        'contact_name': {'write_only': True},
                        'contact_phone': {'write_only': True},
                        'delivery_address': {'write_only': True},
                        'delivery_method': {'write_only': True},
                        'delivery_venue': {'write_only': True},
                        'external_reference': {'write_only': True},
                        'delivery_instructions': {'write_only': True},
                        'prefixed_order_number': {'write_only': True},
                        'formatted_cached_payable_total': {'write_only': True},
                        'payable_total_in_cents': {'write_only': True},
                        'submitted_at': {'write_only': True},
                        'state': {'write_only': True},
                        'placed_by_name': {'write_only': True},
                        # 'delivery_run': {'write_only': True},
                        'delivery_at': {'write_only': True},
                        'delivery_by': {'write_only': True},
                        'delivery_proof_url': {'write_only': True},
                        'locked': {'write_only': True},
                        'created_at': {'write_only': True},
                        'updated_at': {'write_only': True},
                        }

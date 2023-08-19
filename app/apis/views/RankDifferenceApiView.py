import time
from django.core.exceptions import ObjectDoesNotExist
from django.forms import model_to_dict
from django.db.models import Max
from collections import defaultdict

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from core.models import Country

class RankDifferenceApiView(APIView):
    def get(self, request):

        indicator_name =  request.GET.get('indicator')
        countries = str(request.GET.get('countries')).split(';')
        year1 = request.GET.get('year1')        

        # front ikinci ili hemise gondermelidi ki birinci defede suret dusmesin
        if request.GET.get('year2'):
            year2 = request.GET.get('year2')
        else:
            year2= Country.objects.select_related('indicator')\
            .filter(indicator__indicator=indicator_name, country__in=countries).aggregate(max_year=Max('year'))['max_year']
        
        queryset1 = Country.objects.select_related('indicator')\
            .filter(indicator__indicator=indicator_name, 
                    country__in=countries,
                    year=year1).values('amount','country_code','country_code2',"country", "rank")
        
        queryset2 = Country.objects.select_related('indicator')\
            .filter(indicator__indicator=indicator_name, 
                    country__in=countries,
                    year=year2).values('amount','country_code','country_code2',"country", "rank")

        # each_country_rank_diff = []
        
        # for data1, data2 in zip(queryset1, queryset2):
        #     rank_diff = None
        #     if data1.rank is not None and data2.rank is not None:
        #         rank_diff = data1.rank - data2.rank
            
        #     each_country_rank_diff.append({
        #         'country': data1.country,
        #         'year1': year1,
        #         'year2': year2,
        #         'rank1': int(data1.rank),
        #         'rank2': int(data2.rank),
        #         'rank_difference': rank_diff,
        #         'amount1': float(data1.amount),
        #         'amount2': float(data2.amount),
        #     })

        # Create a dictionary to store rank data for year1
        rank_by_country_year1 = {entry["country"]: { 
                                                    'rank':entry["rank"], 
                                                    'amount': entry["amount"]
                                                    } for entry in queryset1}

        # Create a dictionary to store rank data for year2
        rank_by_country_year2 = {entry["country"]: {'country_code':entry["country_code"],
                                                    'country_code_2':entry["country_code2"],
                                                     
                                                    'rank':entry["rank"], 
                                                    'amount': entry['amount']
                                                    } for entry in queryset2}

        # Create a dictionary to store rank difference
        rank_diff_by_country = defaultdict(dict)

        for country in countries:
            # Check if the country has rank data for both years
            if country in rank_by_country_year1 and country in rank_by_country_year2:
                rank_diff_by_country[country] = {
                    'country':country,
                    'country_code':rank_by_country_year2[country]['country_code'],
                    'country_code_2':rank_by_country_year2[country]['country_code_2'],
                    'first_rank' : rank_by_country_year1[country]['rank'],
                    'first_amount' : float(rank_by_country_year1[country]['amount']),
                    'second_rank' : rank_by_country_year2[country]['rank'],
                    'second_amount' : float(rank_by_country_year2[country]['amount']),
                    'rank_difference' : rank_by_country_year1[country]['rank']
                    - rank_by_country_year2[country]['rank'],
                }
                
                
                
        diagram2 = {
            "indicator": indicator_name,
            "first_year": int(year1),
            "second_year": int(year2),
            "countries": rank_diff_by_country
        }

        return Response(diagram2, status=status.HTTP_200_OK)

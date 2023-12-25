import json
from datetime import datetime

import torch
import transformers

from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .serializers import UserSerializer, JournalEntrySerializer, ResultsSerializer
from .models import JournalEntry, Results
from .permissions import IsOwnerOrReadOnly
from ml.model import Model, NewModel

model_naive_bayes = Model.load_model('models/model_00.pkl')
model_bert = NewModel.load_model('models/model_01.bin')
class_names = ['negative', 'neutral', 'positive']
tokenizer = transformers.BertTokenizer.from_pretrained('bert-base-cased')


def sentiread(text: str) -> str:
    encoding = tokenizer.encode_plus(
        text,
        max_length = 256,
        add_special_tokens = True,
        padding = 'max_length',
        return_attention_mask = True,
        return_token_type_ids = False,
        return_tensors='pt'
    )

    output = class_names[torch.argmax(model_bert(encoding['input_ids'], encoding['attention_mask'])).item()]

    return output


def percentages(text: str) -> tuple[float, float, float]:
    "Positive, Negative, Neutral"

    text = text.strip().split('.')
    
    positive = 0
    negative = 0
    neutral = 0

    for sentence in text:
        result = sentiread(sentence)
        if result == 'positive':
            positive += 1
        elif result == 'negative':
            negative += 1
        elif result == 'neutral':
            neutral += 1

    total = positive + negative + neutral

    positive_percentage = positive / total
    negative_percentage = negative / total
    neutral_percentage = neutral / total

    return positive_percentage, negative_percentage, neutral_percentage


@api_view(['POST'])
@permission_classes([AllowAny])
def sentireader(request):
    try:
        json_data = json.loads(request.body)
        input_string = json_data.get('input', '')
    except json.JSONDecodeError:
        input_string = ''

    if not input_string:
        return Response({
            'error': 'Input string is empty'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Naive Bayes
    output_string_naive_bayes = Model.predict(model_naive_bayes, [input_string])

    # BERT nn
    output_string_bert = sentiread(input_string)
    
    response_data = {
        'output_naive': output_string_naive_bayes,
        'output_bert': output_string_bert
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_registration(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data['password'])
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_results(request):
    if request.method == 'POST':
        try:
            results = Results.objects.get(entry=request.data.get('entry'))
            serializer = ResultsSerializer(results)
            return Response(serializer.data)
        except Results.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsOwnerOrReadOnly])
def me(request):
    if isinstance(request.user, AnonymousUser):
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsOwnerOrReadOnly])
def list_journal_entries(request):
    journal_entries = JournalEntry.objects.filter(user=request.user.id)
    serializer = JournalEntrySerializer(journal_entries, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsOwnerOrReadOnly])
def create_journal_entry(request):
    serializer = JournalEntrySerializer(data={
        'entry_text': request.data.get('entry_text'),
        'user': request.user.id
    })
    if serializer.is_valid():
        serializer.save(user=request.user)
        
        positive, negative, neutral = percentages(serializer.data.get('entry_text'))
        entry_id = serializer.data.get('entry_id')

        results_serializer = ResultsSerializer(data={
            'entry': entry_id,
            'positive_percentage': positive,
            'negative_percentage': negative,
            'neutral_percentage': neutral
        })

        if results_serializer.is_valid():
            results_serializer.save()
        
        return Response({
            'entry': serializer.data,
            'result': results_serializer.data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsOwnerOrReadOnly])
def retrieve_update_delete_journal_entry(request, entry_id):
    try:
        journal_entry = JournalEntry.objects.get(entry_id=entry_id)
        results = Results.objects.get(entry=entry_id)
    except JournalEntry.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = JournalEntrySerializer(journal_entry)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = JournalEntrySerializer(journal_entry, data={
            'entry_text': request.data.get('entry_text'),
            'user': request.user.id,
            'datetime': datetime.now()
        })
        if serializer.is_valid():
            serializer.save()
            
            positive, negative, neutral = percentages(serializer.data.get('entry_text'))
            entry_id = serializer.data.get('entry_id')
            results_serializer = ResultsSerializer(results, data={
                'entry': entry_id,
                'positive_percentage': positive,
                'negative_percentage': negative,
                'neutral_percentage': neutral
            })

            if results_serializer.is_valid():
                results_serializer.save()

            return Response({
                'entry': serializer.data,
                'result': results_serializer.data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        journal_entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
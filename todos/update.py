import json
import logging
import os

from pynamodb.exceptions import DoesNotExist
from todos.todo_model import TodoModel


def update(event, context):

    try:
        TodoModel.Meta.table_name = os.environ['DYNAMODB_TABLE']
    except KeyError:
        return {'statusCode': 500,
                'body': json.dumps({'error': 'ENV_VAR_NOT_SET'})}

    try:
        todo_id = event['path']['todo_id']
    except KeyError:
        return {'statusCode': 422,
                'body': json.dumps({'error': 'URL_PARAMETER_MISSING',
                                    'error_message': 'TODO was not found'})}
    try:
        found_todo = TodoModel.get(hash_key=todo_id)
    except DoesNotExist:
        return {'statusCode': 404,
                'body': json.dumps({'error': 'NOT_FOUND',
                                    'error_message': 'TODO was not found'})}

    try:
        # TODO: Figure out why this is behaving differently to the other endpoints
        # Getting type error on the json.loads
        data = json.loads(event['body'])
    except ValueError as err:
        return {'statusCode': 400,
                'body': json.dumps({'error': 'JSON_IRREGULAR',
                                    'error_message': str(err)})}

    if 'text' not in data and 'checked' not in data:
        logging.error('Validation Failed %s', data)
        return {'statusCode': 422,
                'body': json.dumps({'error': 'VALIDATION_FAILED',
                                    'error_message': 'Couldn\'t update the todo item.'})}

    todo_changed = False
    if 'text' in data and data['text'] != found_todo.text:
        found_todo.text = data['text']
        todo_changed = True
    if 'checked' in data and data['checked'] != found_todo.checked:
        found_todo.checked = data['checked']
        todo_changed = True

    if todo_changed:
        found_todo.save()
    else:
        logging.info('Nothing changed did not update')

    # create a response
    return {'statusCode': 200,
            'body': json.dumps(dict(found_todo))}

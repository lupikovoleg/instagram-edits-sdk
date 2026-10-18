#!/usr/bin/env python3
"""Generate the real form-encoded GraphQL transport reference, offline."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOKS = '8dc50e9193c9b70a3f9dbcc25fc5f444bbac27bb56a8c1359ede836b8069c4b8'
VARIABLES = {
    'BaselReelDetailsQuery': {'media_id':'12345','include_creative_tools':False},
    'BaselPublicInsightsQuery': {'media_id':'12345'},
    'BaselAccountLevelInsightsQuery': {'user_id':'999','period':'LAST_30_DAYS','shouldIncludeTimeSeries':True},
    'BaselAccountLevelReelsQuery': {'user_id':'999','first':3,'after':None,'timeframe':'LIFETIME','order_by':'BY_DATE','sort_direction':'DESCENDING','skip_follow_count':False},
    'BaselAudienceInsightsQuery': {'user_id':'999','period':'LAST_30_DAYS','client_timezone':'Europe/Moscow'},
    'XIGBaselAccountLevelReelsDataDeltaQuery': {'media_ids':['12345']},
    'XIGBaselInsightsCommentsQuery': {'media_id':'12345','sort_order':'recent'},
    'BaselKitsQuery': {'after':None},
    'ReelInsightsQuery': {'mediaIgid':'12345','bloksVersioningId':BLOKS},
}
PERIODS = ['LAST_7_DAYS','LAST_14_DAYS','LAST_30_DAYS','LAST_60_DAYS','LAST_90_DAYS','LAST_180_DAYS']


def build():
    operations={o['operation_name']:o for o in json.loads((ROOT/'src/edits_api/operations.json').read_text())}
    examples={}
    schemas={}
    refs=[]
    for name,variables in VARIABLES.items():
        op=operations[name]
        form={'method':'post','pretty':'false','format':'json','server_timestamps':'true','locale':'user',
              'fb_api_req_friendly_name':name,'purpose':'fetch','enable_canonical_naming':'true',
              'enable_canonical_variable_overrides':'true','enable_canonical_naming_ambiguous_type_prefixing':'true',
              'client_doc_id':op['client_doc_id'],'variables':json.dumps(variables,separators=(',',':'))}
        examples[name]={'summary':name,'description':op['live_observation']+'. IDs in this example are synthetic.','value':form}
        properties={}
        for key,value in variables.items():
            if type(value) is bool: prop={'type':'boolean'}
            elif type(value) is int: prop={'type':'integer','minimum':1}
            elif isinstance(value,list):prop={'type':'array','minItems':1,'items':{'type':'string'}}
            elif value is None:prop={'type':['string','null']}
            else:prop={'type':'string'}
            if key=='period':prop['enum']=PERIODS
            if key=='timeframe':prop['enum']=['LIFETIME','ONE_WEEK','TWO_WEEKS','ONE_MONTH','ONE_YEAR']
            if key=='sort_order':prop['enum']=['recent','popular']
            if key=='order_by':prop['enum']=['BY_DATE','BY_VIEWS','BY_LIKES','BY_COMMENTS','BY_REPOSTS','BY_SHARES','BY_SAVES','BY_FOLLOWERS','BY_SKIP_RATE']
            if key=='sort_direction':prop={'type':['string','null'],'enum':['ASCENDING','DESCENDING',None]}
            prop['description']=op['variables'][key]
            properties[key]=prop
        schema_name=name+'Variables'
        schemas[schema_name]={'type':'object','properties':properties,'required':list(variables),'additionalProperties':False,'example':variables,
                              'description':'Object serialized to the JSON string in the variables form field. '+op['live_observation']}
        refs.append({'operation':name,'client_doc_id':op['client_doc_id'],'variables':{'$ref':'#/components/schemas/'+schema_name},'evidence':op['live_semantic_status']})
    properties={key:{'type':'string'} for key in next(iter(examples.values()))['value']}
    properties['fb_api_req_friendly_name']['enum']=list(VARIABLES)
    properties['variables']['description']='JSON serialized as one string, not a nested form object. See named Variables schemas.'
    properties['client_doc_id']['description']='Persisted query ID matching the friendly name; see examples.'
    schemas.update({
        'GraphQLForm':{'type':'object','required':list(properties),'properties':properties},
        'GraphQLResponse':{'type':'object','properties':{'data':{'type':['object','null'],'additionalProperties':True},'errors':{'type':'array','items':{'type':'object','additionalProperties':True}},'hasNext':{'type':'boolean'}},'additionalProperties':True,'description':'Logical paths can appear as canonical keys such as 1$xig_fetch_media(id:$media_id). HTTP 200 can contain GraphQL errors. Some responses are NDJSON incremental patches.'},
        'RetentionPoint':{'type':'object','properties':{'index':{'type':['integer','null']},'value':{'type':['number','null'],'description':'Normalized retention fraction: 1 = 100%; zero is distinct from null.'},'percent':{'type':['number','null']}},'required':['index','value'],'description':'SDK normalized representation; raw API may use 1fvalue.'},
        'ReelSnapshot':{'type':'object','properties':{'media_id':{'type':'string'},'retention_available':{'type':'boolean'},'retention':{'type':'array','items':{'$ref':'#/components/schemas/RetentionPoint'}},'metrics':{'type':'object','additionalProperties':True},'metadata':{'type':'object','additionalProperties':True}},'required':['media_id','retention_available','retention','metrics','metadata'],'description':'Output of SDK ReelInsights.to_dict(), not a separate REST endpoint.'}
    })
    parameters=[]
    for name,example,description in [
        ('User-Agent','Instagram 1.0 Android','Tested fallback client profile.'),
        ('X-IG-App-ID','954255173121948','Edits application ID.'),
        ('IG-INTENDED-USER-ID','999','Current session user ID; example is synthetic.'),
        ('IG-U-DS-USER-ID','999','Current session user ID; example is synthetic.'),
        ('X-FB-Friendly-Name','BaselReelDetailsQuery','Must match fb_api_req_friendly_name in the form.'),
        ('X-Client-Doc-Id',operations['BaselReelDetailsQuery']['client_doc_id'],'Must match client_doc_id in the form.'),
    ]:parameters.append({'name':name,'in':'header','required':True,'schema':{'type':'string'},'example':example,'description':description})
    return {'openapi':'3.1.0','info':{'title':'Instagram Edits internal API — research reference','version':'0.2.0','description':'Unofficial reference, not affiliated with Meta. Nine read operations exercised on one consenting account on 2026-10-18. Comment analysis returned null; Kits was empty. One real POST endpoint with named persisted-query examples. No public REST gateway is provided. Credentials must stay in your backend.'},
        'servers':[{'url':'https://i.instagram.com','description':'Host used in recorded live checks'}],
        'security':[{'InstagramSession':[]}],
        'paths':{'/graphql_www':{'post':{'operationId':'executePersistedInstagramQuery','summary':'Execute a named persisted read query','description':'Choose a request example. Friendly-name and document-ID headers must match its form fields. variables is a JSON string. For operational calls use the Python SDK: it handles aliases, NDJSON, ownership and response validation. Examples contain synthetic account/media IDs.',
            'parameters':parameters,'requestBody':{'required':True,'content':{'application/x-www-form-urlencoded':{'schema':{'$ref':'#/components/schemas/GraphQLForm'},'examples':examples}}},
            'responses':{'200':{'description':'Inspect GraphQL errors and payload availability. Can be a JSON document or NDJSON even with text MIME types.','content':{'application/json':{'schema':{'$ref':'#/components/schemas/GraphQLResponse'}},'text/javascript':{'schema':{'type':'string','description':'JSON document with a text MIME type.'}},'text/html':{'schema':{'type':'string','description':'Observed NDJSON response for ReelInsightsQuery.'}}}},'401':{'description':'Session invalid or expired; do not retry blindly.'},'403':{'description':'Access refused or challenge; no bypass implemented.'},'429':{'description':'Rate limited; stop automated requests.'}},'x-persisted-queries':refs}}},
        'components':{'securitySchemes':{'InstagramSession':{'type':'http','scheme':'bearer','bearerFormat':'IGT:2:<base64 JSON session envelope>','description':'Sensitive session credential, not a public Graph API token. See authentication.md. Do not paste live credentials into the documentation viewer.'}},'schemas':schemas}}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    content=json.dumps(build(),ensure_ascii=False,indent=2)+'\n';path=ROOT/'docs/openapi.json'
    if args.check:
        if not path.exists() or path.read_text()!=content:raise SystemExit('Regenerate OpenAPI with tools/generate_openapi.py')
    else:path.write_text(content)
    print('OpenAPI reference '+('checked' if args.check else 'generated'))


if __name__=='__main__':main()

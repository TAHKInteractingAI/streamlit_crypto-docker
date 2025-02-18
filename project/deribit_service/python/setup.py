# coding: utf-8

"""
    Deribit API

    #Overview  Deribit provides three different interfaces to access the API:  * [JSON-RPC over Websocket](#json-rpc) * [JSON-RPC over HTTP](#json-rpc) * [FIX](#fix-api) (Financial Information eXchange)  With the API Console you can use and test the JSON-RPC API, both via HTTP and  via Websocket. To visit the API console, go to __Account > API tab >  API Console tab.__   ##Naming Deribit tradeable assets or instruments use the following system of naming:  |Kind|Examples|Template|Comments| |----|--------|--------|--------| |Future|<code>BTC-25MAR16</code>, <code>BTC-5AUG16</code>|<code>BTC-DMMMYY</code>|<code>BTC</code> is currency, <code>DMMMYY</code> is expiration date, <code>D</code> stands for day of month (1 or 2 digits), <code>MMM</code> - month (3 first letters in English), <code>YY</code> stands for year.| |Perpetual|<code>BTC-PERPETUAL</code>                        ||Perpetual contract for currency <code>BTC</code>.| |Option|<code>BTC-25MAR16-420-C</code>, <code>BTC-5AUG16-580-P</code>|<code>BTC-DMMMYY-STRIKE-K</code>|<code>STRIKE</code> is option strike price in USD. Template <code>K</code> is option kind: <code>C</code> for call options or <code>P</code> for put options.|   # JSON-RPC JSON-RPC is a light-weight remote procedure call (RPC) protocol. The  [JSON-RPC specification](https://www.jsonrpc.org/specification) defines the data structures that are used for the messages that are exchanged between client and server, as well as the rules around their processing. JSON-RPC uses JSON (RFC 4627) as data format.  JSON-RPC is transport agnostic: it does not specify which transport mechanism must be used. The Deribit API supports both Websocket (preferred) and HTTP (with limitations: subscriptions are not supported over HTTP).  ## Request messages > An example of a request message:  ```json {     \"jsonrpc\": \"2.0\",     \"id\": 8066,     \"method\": \"public/ticker\",     \"params\": {         \"instrument\": \"BTC-24AUG18-6500-P\"     } } ```  According to the JSON-RPC sepcification the requests must be JSON objects with the following fields.  |Name|Type|Description| |----|----|-----------| |jsonrpc|string|The version of the JSON-RPC spec: \"2.0\"| |id|integer or string|An identifier of the request. If it is included, then the response will contain the same identifier| |method|string|The method to be invoked| |params|object|The parameters values for the method. The field names must match with the expected parameter names. The parameters that are expected are described in the documentation for the methods, below.|  <aside class=\"warning\"> The JSON-RPC specification describes two features that are currently not supported by the API:  <ul> <li>Specification of parameter values by position</li> <li>Batch requests</li> </ul>  </aside>   ## Response messages > An example of a response message:  ```json {     \"jsonrpc\": \"2.0\",     \"id\": 5239,     \"testnet\": false,     \"result\": [         {             \"currency\": \"BTC\",             \"currencyLong\": \"Bitcoin\",             \"minConfirmation\": 2,             \"txFee\": 0.0006,             \"isActive\": true,             \"coinType\": \"BITCOIN\",             \"baseAddress\": null         }     ],     \"usIn\": 1535043730126248,     \"usOut\": 1535043730126250,     \"usDiff\": 2 } ```  The JSON-RPC API always responds with a JSON object with the following fields.   |Name|Type|Description| |----|----|-----------| |id|integer|This is the same id that was sent in the request.| |result|any|If successful, the result of the API call. The format for the result is described with each method.| |error|error object|Only present if there was an error invoking the method. The error object is described below.| |testnet|boolean|Indicates whether the API in use is actually the test API.  <code>false</code> for production server, <code>true</code> for test server.| |usIn|integer|The timestamp when the requests was received (microseconds since the Unix epoch)| |usOut|integer|The timestamp when the response was sent (microseconds since the Unix epoch)| |usDiff|integer|The number of microseconds that was spent handling the request|  <aside class=\"notice\"> The fields <code>testnet</code>, <code>usIn</code>, <code>usOut</code> and <code>usDiff</code> are not part of the JSON-RPC standard.  <p>In order not to clutter the examples they will generally be omitted from the example code.</p> </aside>  > An example of a response with an error:  ```json {     \"jsonrpc\": \"2.0\",     \"id\": 8163,     \"error\": {         \"code\": 11050,         \"message\": \"bad_request\"     },     \"testnet\": false,     \"usIn\": 1535037392434763,     \"usOut\": 1535037392448119,     \"usDiff\": 13356 } ``` In case of an error the response message will contain the error field, with as value an object with the following with the following fields:  |Name|Type|Description |----|----|-----------| |code|integer|A number that indicates the kind of error.| |message|string|A short description that indicates the kind of error.| |data|any|Additional data about the error. This field may be omitted.|  ## Notifications  > An example of a notification:  ```json {     \"jsonrpc\": \"2.0\",     \"method\": \"subscription\",     \"params\": {         \"channel\": \"deribit_price_index.btc_usd\",         \"data\": {             \"timestamp\": 1535098298227,             \"price\": 6521.17,             \"index_name\": \"btc_usd\"         }     } } ```  API users can subscribe to certain types of notifications. This means that they will receive JSON-RPC notification-messages from the server when certain events occur, such as changes to the index price or changes to the order book for a certain instrument.   The API methods [public/subscribe](#public-subscribe) and [private/subscribe](#private-subscribe) are used to set up a subscription. Since HTTP does not support the sending of messages from server to client, these methods are only availble when using the Websocket transport mechanism.  At the moment of subscription a \"channel\" must be specified. The channel determines the type of events that will be received.  See [Subscriptions](#subscriptions) for more details about the channels.  In accordance with the JSON-RPC specification, the format of a notification  is that of a request message without an <code>id</code> field. The value of the <code>method</code> field will always be <code>\"subscription\"</code>. The <code>params</code> field will always be an object with 2 members: <code>channel</code> and <code>data</code>. The value of the <code>channel</code> member is the name of the channel (a string). The value of the <code>data</code> member is an object that contains data  that is specific for the channel.   ## Authentication  > An example of a JSON request with token:  ```json {     \"id\": 5647,     \"method\": \"private/get_subaccounts\",     \"params\": {         \"access_token\": \"67SVutDoVZSzkUStHSuk51WntMNBJ5mh5DYZhwzpiqDF\"     } } ```  The API consists of `public` and `private` methods. The public methods do not require authentication. The private methods use OAuth 2.0 authentication. This means that a valid OAuth access token must be included in the request, which can get achived by calling method [public/auth](#public-auth).  When the token was assigned to the user, it should be passed along, with other request parameters, back to the server:  |Connection type|Access token placement |----|-----------| |**Websocket**|Inside request JSON parameters, as an `access_token` field| |**HTTP (REST)**|Header `Authorization: bearer ```Token``` ` value|  ### Additional authorization method - basic user credentials  <span style=\"color:red\"><b> ! Not recommended - however, it could be useful for quick testing API</b></span></br>  Every `private` method could be accessed by providing, inside HTTP `Authorization: Basic XXX` header, values with user `ClientId` and assigned `ClientSecret` (both values can be found on the API page on the Deribit website) encoded with `Base64`:  <code>Authorization: Basic BASE64(`ClientId` + `:` + `ClientSecret`)</code>   ### Additional authorization method - Deribit signature credentials  The Derbit service provides dedicated authorization method, which harness user generated signature to increase security level for passing request data. Generated value is passed inside `Authorization` header, coded as:  <code>Authorization: deri-hmac-sha256 id=```ClientId```,ts=```Timestamp```,sig=```Signature```,nonce=```Nonce```</code>  where:  |Deribit credential|Description |----|-----------| |*ClientId*|Can be found on the API page on the Deribit website| |*Timestamp*|Time when the request was generated - given as **miliseconds**. It's valid for **60 seconds** since generation, after that time any request with an old timestamp will be rejected.| |*Signature*|Value for signature calculated as described below | |*Nonce*|Single usage, user generated initialization vector for the server token|  The signature is generated by the following formula:  <code> Signature = HEX_STRING( HMAC-SHA256( ClientSecret, StringToSign ) );</code></br>  <code> StringToSign =  Timestamp + \"\\n\" + Nonce + \"\\n\" + RequestData;</code></br>  <code> RequestData =  UPPERCASE(HTTP_METHOD())  + \"\\n\" + URI() + \"\\n\" + RequestBody + \"\\n\";</code></br>   e.g. (using shell with ```openssl``` tool):  <code>&nbsp;&nbsp;&nbsp;&nbsp;ClientId=AAAAAAAAAAA</code></br>  <code>&nbsp;&nbsp;&nbsp;&nbsp;ClientSecret=ABCD</code></br>  <code>&nbsp;&nbsp;&nbsp;&nbsp;Timestamp=$( date +%s000 )</code></br>  <code>&nbsp;&nbsp;&nbsp;&nbsp;Nonce=$( cat /dev/urandom | tr -dc 'a-z0-9' | head -c8 )</code></br>  <code>&nbsp;&nbsp;&nbsp;&nbsp;URI=\"/api/v2/private/get_account_summary?currency=BTC\"</code></br>  <code>&nbsp;&nbsp;&nbsp;&nbsp;HttpMethod=GET</code></br>  <code>&nbsp;&nbsp;&nbsp;&nbsp;Body=\"\"</code></br></br>  <code>&nbsp;&nbsp;&nbsp;&nbsp;Signature=$( echo -ne \"${Timestamp}\\n${Nonce}\\n${HttpMethod}\\n${URI}\\n${Body}\\n\" | openssl sha256 -r -hmac \"$ClientSecret\" | cut -f1 -d' ' )</code></br></br> <code>&nbsp;&nbsp;&nbsp;&nbsp;echo $Signature</code></br></br>  <code>&nbsp;&nbsp;&nbsp;&nbsp;shell output> ea40d5e5e4fae235ab22b61da98121fbf4acdc06db03d632e23c66bcccb90d2c  (**WARNING**: Exact value depends on current timestamp and client credentials</code></br></br>  <code>&nbsp;&nbsp;&nbsp;&nbsp;curl -s -X ${HttpMethod} -H \"Authorization: deri-hmac-sha256 id=${ClientId},ts=${Timestamp},nonce=${Nonce},sig=${Signature}\" \"https://www.deribit.com${URI}\"</code></br></br>    ### Additional authorization method - signature credentials (WebSocket API)  When connecting through Websocket, user can request for authorization using ```client_credential``` method, which requires providing following parameters (as a part of JSON request):  |JSON parameter|Description |----|-----------| |*grant_type*|Must be **client_signature**| |*client_id*|Can be found on the API page on the Deribit website| |*timestamp*|Time when the request was generated - given as **miliseconds**. It's valid for **60 seconds** since generation, after that time any request with an old timestamp will be rejected.| |*signature*|Value for signature calculated as described below | |*nonce*|Single usage, user generated initialization vector for the server token| |*data*|**Optional** field, which contains any user specific value|  The signature is generated by the following formula:  <code> StringToSign =  Timestamp + \"\\n\" + Nonce + \"\\n\" + Data;</code></br>  <code> Signature = HEX_STRING( HMAC-SHA256( ClientSecret, StringToSign ) );</code></br>   e.g. (using shell with ```openssl``` tool):  <code>&nbsp;&nbsp;&nbsp;&nbsp;ClientId=AAAAAAAAAAA</code></br>  <code>&nbsp;&nbsp;&nbsp;&nbsp;ClientSecret=ABCD</code></br>  <code>&nbsp;&nbsp;&nbsp;&nbsp;Timestamp=$( date +%s000 ) # e.g. 1554883365000 </code></br>  <code>&nbsp;&nbsp;&nbsp;&nbsp;Nonce=$( cat /dev/urandom | tr -dc 'a-z0-9' | head -c8 ) # e.g. fdbmmz79 </code></br>  <code>&nbsp;&nbsp;&nbsp;&nbsp;Data=\"\"</code></br></br>  <code>&nbsp;&nbsp;&nbsp;&nbsp;Signature=$( echo -ne \"${Timestamp}\\n${Nonce}\\n${Data}\\n\" | openssl sha256 -r -hmac \"$ClientSecret\" | cut -f1 -d' ' )</code></br></br> <code>&nbsp;&nbsp;&nbsp;&nbsp;echo $Signature</code></br></br>  <code>&nbsp;&nbsp;&nbsp;&nbsp;shell output> e20c9cd5639d41f8bbc88f4d699c4baf94a4f0ee320e9a116b72743c449eb994  (**WARNING**: Exact value depends on current timestamp and client credentials</code></br></br>   You can also check the signature value using some online tools like, e.g: [https://codebeautify.org/hmac-generator](https://codebeautify.org/hmac-generator) (but don't forget about adding *newline* after each part of the hashed text and remember that you **should use** it only with your **test credentials**).   Here's a sample JSON request created using the values from the example above:  <code> {                            </br> &nbsp;&nbsp;\"jsonrpc\" : \"2.0\",         </br> &nbsp;&nbsp;\"id\" : 9929,               </br> &nbsp;&nbsp;\"method\" : \"public/auth\",  </br> &nbsp;&nbsp;\"params\" :                 </br> &nbsp;&nbsp;{                        </br> &nbsp;&nbsp;&nbsp;&nbsp;\"grant_type\" : \"client_signature\",   </br> &nbsp;&nbsp;&nbsp;&nbsp;\"client_id\" : \"AAAAAAAAAAA\",         </br> &nbsp;&nbsp;&nbsp;&nbsp;\"timestamp\": \"1554883365000\",        </br> &nbsp;&nbsp;&nbsp;&nbsp;\"nonce\": \"fdbmmz79\",                 </br> &nbsp;&nbsp;&nbsp;&nbsp;\"data\": \"\",                          </br> &nbsp;&nbsp;&nbsp;&nbsp;\"signature\" : \"e20c9cd5639d41f8bbc88f4d699c4baf94a4f0ee320e9a116b72743c449eb994\"  </br> &nbsp;&nbsp;}                        </br> }                            </br> </code>   ### Access scope  When asking for `access token` user can provide the required access level (called `scope`) which defines what type of functionality he/she wants to use, and whether requests are only going to check for some data or also to update them.  Scopes are required and checked for `private` methods, so if you plan to use only `public` information you can stay with values assigned by default.  |Scope|Description |----|-----------| |*account:read*|Access to **account** methods - read only data| |*account:read_write*|Access to **account** methods - allows to manage account settings, add subaccounts, etc.| |*trade:read*|Access to **trade** methods - read only data| |*trade:read_write*|Access to **trade** methods - required to create and modify orders| |*wallet:read*|Access to **wallet** methods - read only data| |*wallet:read_write*|Access to **wallet** methods - allows to withdraw, generate new deposit address, etc.| |*wallet:none*, *account:none*, *trade:none*|Blocked access to specified functionality|    <span style=\"color:red\">**NOTICE:**</span> Depending on choosing an authentication method (```grant type```) some scopes could be narrowed by the server. e.g. when ```grant_type = client_credentials``` and ```scope = wallet:read_write``` it's modified by the server as ```scope = wallet:read```\"   ## JSON-RPC over websocket Websocket is the prefered transport mechanism for the JSON-RPC API, because it is faster and because it can support [subscriptions](#subscriptions) and [cancel on disconnect](#private-enable_cancel_on_disconnect). The code examples that can be found next to each of the methods show how websockets can be used from Python or Javascript/node.js.  ## JSON-RPC over HTTP Besides websockets it is also possible to use the API via HTTP. The code examples for 'shell' show how this can be done using curl. Note that subscriptions and cancel on disconnect are not supported via HTTP.  #Methods   # noqa: E501

    The version of the OpenAPI document: 2.0.0
    Generated by: https://openapi-generator.tech
"""


from setuptools import setup, find_packages  # noqa: H301

NAME = "openapi-client"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["urllib3 >= 1.15", "six >= 1.10", "certifi", "python-dateutil"]

setup(
    name=NAME,
    version=VERSION,
    description="Deribit API",
    author_email="",
    url="",
    keywords=["OpenAPI", "OpenAPI-Generator", "Deribit API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    #Overview  Deribit provides three different interfaces to access the API:  * [JSON-RPC over Websocket](#json-rpc) * [JSON-RPC over HTTP](#json-rpc) * [FIX](#fix-api) (Financial Information eXchange)  With the API Console you can use and test the JSON-RPC API, both via HTTP and  via Websocket. To visit the API console, go to __Account &gt; API tab &gt;  API Console tab.__   ##Naming Deribit tradeable assets or instruments use the following system of naming:  |Kind|Examples|Template|Comments| |----|--------|--------|--------| |Future|&lt;code&gt;BTC-25MAR16&lt;/code&gt;, &lt;code&gt;BTC-5AUG16&lt;/code&gt;|&lt;code&gt;BTC-DMMMYY&lt;/code&gt;|&lt;code&gt;BTC&lt;/code&gt; is currency, &lt;code&gt;DMMMYY&lt;/code&gt; is expiration date, &lt;code&gt;D&lt;/code&gt; stands for day of month (1 or 2 digits), &lt;code&gt;MMM&lt;/code&gt; - month (3 first letters in English), &lt;code&gt;YY&lt;/code&gt; stands for year.| |Perpetual|&lt;code&gt;BTC-PERPETUAL&lt;/code&gt;                        ||Perpetual contract for currency &lt;code&gt;BTC&lt;/code&gt;.| |Option|&lt;code&gt;BTC-25MAR16-420-C&lt;/code&gt;, &lt;code&gt;BTC-5AUG16-580-P&lt;/code&gt;|&lt;code&gt;BTC-DMMMYY-STRIKE-K&lt;/code&gt;|&lt;code&gt;STRIKE&lt;/code&gt; is option strike price in USD. Template &lt;code&gt;K&lt;/code&gt; is option kind: &lt;code&gt;C&lt;/code&gt; for call options or &lt;code&gt;P&lt;/code&gt; for put options.|   # JSON-RPC JSON-RPC is a light-weight remote procedure call (RPC) protocol. The  [JSON-RPC specification](https://www.jsonrpc.org/specification) defines the data structures that are used for the messages that are exchanged between client and server, as well as the rules around their processing. JSON-RPC uses JSON (RFC 4627) as data format.  JSON-RPC is transport agnostic: it does not specify which transport mechanism must be used. The Deribit API supports both Websocket (preferred) and HTTP (with limitations: subscriptions are not supported over HTTP).  ## Request messages &gt; An example of a request message:  &#x60;&#x60;&#x60;json {     \&quot;jsonrpc\&quot;: \&quot;2.0\&quot;,     \&quot;id\&quot;: 8066,     \&quot;method\&quot;: \&quot;public/ticker\&quot;,     \&quot;params\&quot;: {         \&quot;instrument\&quot;: \&quot;BTC-24AUG18-6500-P\&quot;     } } &#x60;&#x60;&#x60;  According to the JSON-RPC sepcification the requests must be JSON objects with the following fields.  |Name|Type|Description| |----|----|-----------| |jsonrpc|string|The version of the JSON-RPC spec: \&quot;2.0\&quot;| |id|integer or string|An identifier of the request. If it is included, then the response will contain the same identifier| |method|string|The method to be invoked| |params|object|The parameters values for the method. The field names must match with the expected parameter names. The parameters that are expected are described in the documentation for the methods, below.|  &lt;aside class&#x3D;\&quot;warning\&quot;&gt; The JSON-RPC specification describes two features that are currently not supported by the API:  &lt;ul&gt; &lt;li&gt;Specification of parameter values by position&lt;/li&gt; &lt;li&gt;Batch requests&lt;/li&gt; &lt;/ul&gt;  &lt;/aside&gt;   ## Response messages &gt; An example of a response message:  &#x60;&#x60;&#x60;json {     \&quot;jsonrpc\&quot;: \&quot;2.0\&quot;,     \&quot;id\&quot;: 5239,     \&quot;testnet\&quot;: false,     \&quot;result\&quot;: [         {             \&quot;currency\&quot;: \&quot;BTC\&quot;,             \&quot;currencyLong\&quot;: \&quot;Bitcoin\&quot;,             \&quot;minConfirmation\&quot;: 2,             \&quot;txFee\&quot;: 0.0006,             \&quot;isActive\&quot;: true,             \&quot;coinType\&quot;: \&quot;BITCOIN\&quot;,             \&quot;baseAddress\&quot;: null         }     ],     \&quot;usIn\&quot;: 1535043730126248,     \&quot;usOut\&quot;: 1535043730126250,     \&quot;usDiff\&quot;: 2 } &#x60;&#x60;&#x60;  The JSON-RPC API always responds with a JSON object with the following fields.   |Name|Type|Description| |----|----|-----------| |id|integer|This is the same id that was sent in the request.| |result|any|If successful, the result of the API call. The format for the result is described with each method.| |error|error object|Only present if there was an error invoking the method. The error object is described below.| |testnet|boolean|Indicates whether the API in use is actually the test API.  &lt;code&gt;false&lt;/code&gt; for production server, &lt;code&gt;true&lt;/code&gt; for test server.| |usIn|integer|The timestamp when the requests was received (microseconds since the Unix epoch)| |usOut|integer|The timestamp when the response was sent (microseconds since the Unix epoch)| |usDiff|integer|The number of microseconds that was spent handling the request|  &lt;aside class&#x3D;\&quot;notice\&quot;&gt; The fields &lt;code&gt;testnet&lt;/code&gt;, &lt;code&gt;usIn&lt;/code&gt;, &lt;code&gt;usOut&lt;/code&gt; and &lt;code&gt;usDiff&lt;/code&gt; are not part of the JSON-RPC standard.  &lt;p&gt;In order not to clutter the examples they will generally be omitted from the example code.&lt;/p&gt; &lt;/aside&gt;  &gt; An example of a response with an error:  &#x60;&#x60;&#x60;json {     \&quot;jsonrpc\&quot;: \&quot;2.0\&quot;,     \&quot;id\&quot;: 8163,     \&quot;error\&quot;: {         \&quot;code\&quot;: 11050,         \&quot;message\&quot;: \&quot;bad_request\&quot;     },     \&quot;testnet\&quot;: false,     \&quot;usIn\&quot;: 1535037392434763,     \&quot;usOut\&quot;: 1535037392448119,     \&quot;usDiff\&quot;: 13356 } &#x60;&#x60;&#x60; In case of an error the response message will contain the error field, with as value an object with the following with the following fields:  |Name|Type|Description |----|----|-----------| |code|integer|A number that indicates the kind of error.| |message|string|A short description that indicates the kind of error.| |data|any|Additional data about the error. This field may be omitted.|  ## Notifications  &gt; An example of a notification:  &#x60;&#x60;&#x60;json {     \&quot;jsonrpc\&quot;: \&quot;2.0\&quot;,     \&quot;method\&quot;: \&quot;subscription\&quot;,     \&quot;params\&quot;: {         \&quot;channel\&quot;: \&quot;deribit_price_index.btc_usd\&quot;,         \&quot;data\&quot;: {             \&quot;timestamp\&quot;: 1535098298227,             \&quot;price\&quot;: 6521.17,             \&quot;index_name\&quot;: \&quot;btc_usd\&quot;         }     } } &#x60;&#x60;&#x60;  API users can subscribe to certain types of notifications. This means that they will receive JSON-RPC notification-messages from the server when certain events occur, such as changes to the index price or changes to the order book for a certain instrument.   The API methods [public/subscribe](#public-subscribe) and [private/subscribe](#private-subscribe) are used to set up a subscription. Since HTTP does not support the sending of messages from server to client, these methods are only availble when using the Websocket transport mechanism.  At the moment of subscription a \&quot;channel\&quot; must be specified. The channel determines the type of events that will be received.  See [Subscriptions](#subscriptions) for more details about the channels.  In accordance with the JSON-RPC specification, the format of a notification  is that of a request message without an &lt;code&gt;id&lt;/code&gt; field. The value of the &lt;code&gt;method&lt;/code&gt; field will always be &lt;code&gt;\&quot;subscription\&quot;&lt;/code&gt;. The &lt;code&gt;params&lt;/code&gt; field will always be an object with 2 members: &lt;code&gt;channel&lt;/code&gt; and &lt;code&gt;data&lt;/code&gt;. The value of the &lt;code&gt;channel&lt;/code&gt; member is the name of the channel (a string). The value of the &lt;code&gt;data&lt;/code&gt; member is an object that contains data  that is specific for the channel.   ## Authentication  &gt; An example of a JSON request with token:  &#x60;&#x60;&#x60;json {     \&quot;id\&quot;: 5647,     \&quot;method\&quot;: \&quot;private/get_subaccounts\&quot;,     \&quot;params\&quot;: {         \&quot;access_token\&quot;: \&quot;67SVutDoVZSzkUStHSuk51WntMNBJ5mh5DYZhwzpiqDF\&quot;     } } &#x60;&#x60;&#x60;  The API consists of &#x60;public&#x60; and &#x60;private&#x60; methods. The public methods do not require authentication. The private methods use OAuth 2.0 authentication. This means that a valid OAuth access token must be included in the request, which can get achived by calling method [public/auth](#public-auth).  When the token was assigned to the user, it should be passed along, with other request parameters, back to the server:  |Connection type|Access token placement |----|-----------| |**Websocket**|Inside request JSON parameters, as an &#x60;access_token&#x60; field| |**HTTP (REST)**|Header &#x60;Authorization: bearer &#x60;&#x60;&#x60;Token&#x60;&#x60;&#x60; &#x60; value|  ### Additional authorization method - basic user credentials  &lt;span style&#x3D;\&quot;color:red\&quot;&gt;&lt;b&gt; ! Not recommended - however, it could be useful for quick testing API&lt;/b&gt;&lt;/span&gt;&lt;/br&gt;  Every &#x60;private&#x60; method could be accessed by providing, inside HTTP &#x60;Authorization: Basic XXX&#x60; header, values with user &#x60;ClientId&#x60; and assigned &#x60;ClientSecret&#x60; (both values can be found on the API page on the Deribit website) encoded with &#x60;Base64&#x60;:  &lt;code&gt;Authorization: Basic BASE64(&#x60;ClientId&#x60; + &#x60;:&#x60; + &#x60;ClientSecret&#x60;)&lt;/code&gt;   ### Additional authorization method - Deribit signature credentials  The Derbit service provides dedicated authorization method, which harness user generated signature to increase security level for passing request data. Generated value is passed inside &#x60;Authorization&#x60; header, coded as:  &lt;code&gt;Authorization: deri-hmac-sha256 id&#x3D;&#x60;&#x60;&#x60;ClientId&#x60;&#x60;&#x60;,ts&#x3D;&#x60;&#x60;&#x60;Timestamp&#x60;&#x60;&#x60;,sig&#x3D;&#x60;&#x60;&#x60;Signature&#x60;&#x60;&#x60;,nonce&#x3D;&#x60;&#x60;&#x60;Nonce&#x60;&#x60;&#x60;&lt;/code&gt;  where:  |Deribit credential|Description |----|-----------| |*ClientId*|Can be found on the API page on the Deribit website| |*Timestamp*|Time when the request was generated - given as **miliseconds**. It&#39;s valid for **60 seconds** since generation, after that time any request with an old timestamp will be rejected.| |*Signature*|Value for signature calculated as described below | |*Nonce*|Single usage, user generated initialization vector for the server token|  The signature is generated by the following formula:  &lt;code&gt; Signature &#x3D; HEX_STRING( HMAC-SHA256( ClientSecret, StringToSign ) );&lt;/code&gt;&lt;/br&gt;  &lt;code&gt; StringToSign &#x3D;  Timestamp + \&quot;\\n\&quot; + Nonce + \&quot;\\n\&quot; + RequestData;&lt;/code&gt;&lt;/br&gt;  &lt;code&gt; RequestData &#x3D;  UPPERCASE(HTTP_METHOD())  + \&quot;\\n\&quot; + URI() + \&quot;\\n\&quot; + RequestBody + \&quot;\\n\&quot;;&lt;/code&gt;&lt;/br&gt;   e.g. (using shell with &#x60;&#x60;&#x60;openssl&#x60;&#x60;&#x60; tool):  &lt;code&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;ClientId&#x3D;AAAAAAAAAAA&lt;/code&gt;&lt;/br&gt;  &lt;code&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;ClientSecret&#x3D;ABCD&lt;/code&gt;&lt;/br&gt;  &lt;code&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;Timestamp&#x3D;$( date +%s000 )&lt;/code&gt;&lt;/br&gt;  &lt;code&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;Nonce&#x3D;$( cat /dev/urandom | tr -dc &#39;a-z0-9&#39; | head -c8 )&lt;/code&gt;&lt;/br&gt;  &lt;code&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;URI&#x3D;\&quot;/api/v2/private/get_account_summary?currency&#x3D;BTC\&quot;&lt;/code&gt;&lt;/br&gt;  &lt;code&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;HttpMethod&#x3D;GET&lt;/code&gt;&lt;/br&gt;  &lt;code&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;Body&#x3D;\&quot;\&quot;&lt;/code&gt;&lt;/br&gt;&lt;/br&gt;  &lt;code&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;Signature&#x3D;$( echo -ne \&quot;${Timestamp}\\n${Nonce}\\n${HttpMethod}\\n${URI}\\n${Body}\\n\&quot; | openssl sha256 -r -hmac \&quot;$ClientSecret\&quot; | cut -f1 -d&#39; &#39; )&lt;/code&gt;&lt;/br&gt;&lt;/br&gt; &lt;code&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;echo $Signature&lt;/code&gt;&lt;/br&gt;&lt;/br&gt;  &lt;code&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;shell output&gt; ea40d5e5e4fae235ab22b61da98121fbf4acdc06db03d632e23c66bcccb90d2c  (**WARNING**: Exact value depends on current timestamp and client credentials&lt;/code&gt;&lt;/br&gt;&lt;/br&gt;  &lt;code&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;curl -s -X ${HttpMethod} -H \&quot;Authorization: deri-hmac-sha256 id&#x3D;${ClientId},ts&#x3D;${Timestamp},nonce&#x3D;${Nonce},sig&#x3D;${Signature}\&quot; \&quot;https://www.deribit.com${URI}\&quot;&lt;/code&gt;&lt;/br&gt;&lt;/br&gt;    ### Additional authorization method - signature credentials (WebSocket API)  When connecting through Websocket, user can request for authorization using &#x60;&#x60;&#x60;client_credential&#x60;&#x60;&#x60; method, which requires providing following parameters (as a part of JSON request):  |JSON parameter|Description |----|-----------| |*grant_type*|Must be **client_signature**| |*client_id*|Can be found on the API page on the Deribit website| |*timestamp*|Time when the request was generated - given as **miliseconds**. It&#39;s valid for **60 seconds** since generation, after that time any request with an old timestamp will be rejected.| |*signature*|Value for signature calculated as described below | |*nonce*|Single usage, user generated initialization vector for the server token| |*data*|**Optional** field, which contains any user specific value|  The signature is generated by the following formula:  &lt;code&gt; StringToSign &#x3D;  Timestamp + \&quot;\\n\&quot; + Nonce + \&quot;\\n\&quot; + Data;&lt;/code&gt;&lt;/br&gt;  &lt;code&gt; Signature &#x3D; HEX_STRING( HMAC-SHA256( ClientSecret, StringToSign ) );&lt;/code&gt;&lt;/br&gt;   e.g. (using shell with &#x60;&#x60;&#x60;openssl&#x60;&#x60;&#x60; tool):  &lt;code&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;ClientId&#x3D;AAAAAAAAAAA&lt;/code&gt;&lt;/br&gt;  &lt;code&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;ClientSecret&#x3D;ABCD&lt;/code&gt;&lt;/br&gt;  &lt;code&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;Timestamp&#x3D;$( date +%s000 ) # e.g. 1554883365000 &lt;/code&gt;&lt;/br&gt;  &lt;code&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;Nonce&#x3D;$( cat /dev/urandom | tr -dc &#39;a-z0-9&#39; | head -c8 ) # e.g. fdbmmz79 &lt;/code&gt;&lt;/br&gt;  &lt;code&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;Data&#x3D;\&quot;\&quot;&lt;/code&gt;&lt;/br&gt;&lt;/br&gt;  &lt;code&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;Signature&#x3D;$( echo -ne \&quot;${Timestamp}\\n${Nonce}\\n${Data}\\n\&quot; | openssl sha256 -r -hmac \&quot;$ClientSecret\&quot; | cut -f1 -d&#39; &#39; )&lt;/code&gt;&lt;/br&gt;&lt;/br&gt; &lt;code&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;echo $Signature&lt;/code&gt;&lt;/br&gt;&lt;/br&gt;  &lt;code&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;shell output&gt; e20c9cd5639d41f8bbc88f4d699c4baf94a4f0ee320e9a116b72743c449eb994  (**WARNING**: Exact value depends on current timestamp and client credentials&lt;/code&gt;&lt;/br&gt;&lt;/br&gt;   You can also check the signature value using some online tools like, e.g: [https://codebeautify.org/hmac-generator](https://codebeautify.org/hmac-generator) (but don&#39;t forget about adding *newline* after each part of the hashed text and remember that you **should use** it only with your **test credentials**).   Here&#39;s a sample JSON request created using the values from the example above:  &lt;code&gt; {                            &lt;/br&gt; &amp;nbsp;&amp;nbsp;\&quot;jsonrpc\&quot; : \&quot;2.0\&quot;,         &lt;/br&gt; &amp;nbsp;&amp;nbsp;\&quot;id\&quot; : 9929,               &lt;/br&gt; &amp;nbsp;&amp;nbsp;\&quot;method\&quot; : \&quot;public/auth\&quot;,  &lt;/br&gt; &amp;nbsp;&amp;nbsp;\&quot;params\&quot; :                 &lt;/br&gt; &amp;nbsp;&amp;nbsp;{                        &lt;/br&gt; &amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;\&quot;grant_type\&quot; : \&quot;client_signature\&quot;,   &lt;/br&gt; &amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;\&quot;client_id\&quot; : \&quot;AAAAAAAAAAA\&quot;,         &lt;/br&gt; &amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;\&quot;timestamp\&quot;: \&quot;1554883365000\&quot;,        &lt;/br&gt; &amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;\&quot;nonce\&quot;: \&quot;fdbmmz79\&quot;,                 &lt;/br&gt; &amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;\&quot;data\&quot;: \&quot;\&quot;,                          &lt;/br&gt; &amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;\&quot;signature\&quot; : \&quot;e20c9cd5639d41f8bbc88f4d699c4baf94a4f0ee320e9a116b72743c449eb994\&quot;  &lt;/br&gt; &amp;nbsp;&amp;nbsp;}                        &lt;/br&gt; }                            &lt;/br&gt; &lt;/code&gt;   ### Access scope  When asking for &#x60;access token&#x60; user can provide the required access level (called &#x60;scope&#x60;) which defines what type of functionality he/she wants to use, and whether requests are only going to check for some data or also to update them.  Scopes are required and checked for &#x60;private&#x60; methods, so if you plan to use only &#x60;public&#x60; information you can stay with values assigned by default.  |Scope|Description |----|-----------| |*account:read*|Access to **account** methods - read only data| |*account:read_write*|Access to **account** methods - allows to manage account settings, add subaccounts, etc.| |*trade:read*|Access to **trade** methods - read only data| |*trade:read_write*|Access to **trade** methods - required to create and modify orders| |*wallet:read*|Access to **wallet** methods - read only data| |*wallet:read_write*|Access to **wallet** methods - allows to withdraw, generate new deposit address, etc.| |*wallet:none*, *account:none*, *trade:none*|Blocked access to specified functionality|    &lt;span style&#x3D;\&quot;color:red\&quot;&gt;**NOTICE:**&lt;/span&gt; Depending on choosing an authentication method (&#x60;&#x60;&#x60;grant type&#x60;&#x60;&#x60;) some scopes could be narrowed by the server. e.g. when &#x60;&#x60;&#x60;grant_type &#x3D; client_credentials&#x60;&#x60;&#x60; and &#x60;&#x60;&#x60;scope &#x3D; wallet:read_write&#x60;&#x60;&#x60; it&#39;s modified by the server as &#x60;&#x60;&#x60;scope &#x3D; wallet:read&#x60;&#x60;&#x60;\&quot;   ## JSON-RPC over websocket Websocket is the prefered transport mechanism for the JSON-RPC API, because it is faster and because it can support [subscriptions](#subscriptions) and [cancel on disconnect](#private-enable_cancel_on_disconnect). The code examples that can be found next to each of the methods show how websockets can be used from Python or Javascript/node.js.  ## JSON-RPC over HTTP Besides websockets it is also possible to use the API via HTTP. The code examples for &#39;shell&#39; show how this can be done using curl. Note that subscriptions and cancel on disconnect are not supported via HTTP.  #Methods   # noqa: E501
    """
)

# Protocol Documentation

<a name="top"></a>

## Table of Contents

- [common/v1/common.proto](#common_v1_common-proto)
    - [Empty](#common-v1-Empty)

- [shortener/v1/shortener.proto](#shortener_v1_shortener-proto)
    - [CreateShortUrlRequest](#shortener-v1-CreateShortUrlRequest)
    - [CreateShortUrlResponse](#shortener-v1-CreateShortUrlResponse)
    - [DeleteUrlRequest](#shortener-v1-DeleteUrlRequest)
    - [DeleteUrlResponse](#shortener-v1-DeleteUrlResponse)
    - [ResolveKeyRequest](#shortener-v1-ResolveKeyRequest)
    - [ResolveKeyResponse](#shortener-v1-ResolveKeyResponse)
    - [UpdateUrlRequest](#shortener-v1-UpdateUrlRequest)
    - [UpdateUrlResponse](#shortener-v1-UpdateUrlResponse)

    - [ShortenerService](#shortener-v1-ShortenerService)

- [user_urls/v1/user_urls.proto](#user_urls_v1_user_urls-proto)
    - [GetUserUrlsRequest](#user_urls-v1-GetUserUrlsRequest)
    - [GetUserUrlsResponse](#user_urls-v1-GetUserUrlsResponse)
    - [UserUrl](#user_urls-v1-UserUrl)

    - [UserUrlsService](#user_urls-v1-UserUrlsService)

- [Scalar Value Types](#scalar-value-types)

<a name="common_v1_common-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## common/v1/common.proto

<a name="common-v1-Empty"></a>

### Empty

<a name="shortener_v1_shortener-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## shortener/v1/shortener.proto

Shortener related messages.

<a name="shortener-v1-CreateShortUrlRequest"></a>

### CreateShortUrlRequest

| Field      | Type              | Label | Description  |
|------------|-------------------|-------|--------------|
| target_url | [string](#string) |       | Original URL |

<a name="shortener-v1-CreateShortUrlResponse"></a>

### CreateShortUrlResponse

| Field      | Type              | Label | Description              |
|------------|-------------------|-------|--------------------------|
| key        | [string](#string) |       | Short key                |
| target_url | [string](#string) |       | Unique booking status ID |

<a name="shortener-v1-DeleteUrlRequest"></a>

### DeleteUrlRequest

| Field | Type              | Label | Description |
|-------|-------------------|-------|-------------|
| key   | [string](#string) |       | Short key   |

<a name="shortener-v1-DeleteUrlResponse"></a>

### DeleteUrlResponse

| Field | Type              | Label | Description     |
|-------|-------------------|-------|-----------------|
| ok    | [string](#string) |       | response result |

<a name="shortener-v1-ResolveKeyRequest"></a>

### ResolveKeyRequest

| Field | Type              | Label | Description |
|-------|-------------------|-------|-------------|
| key   | [string](#string) |       | Short key   |

<a name="shortener-v1-ResolveKeyResponse"></a>

### ResolveKeyResponse

| Field      | Type              | Label | Description  |
|------------|-------------------|-------|--------------|
| target_url | [string](#string) |       | Original URL |

<a name="shortener-v1-UpdateUrlRequest"></a>

### UpdateUrlRequest

| Field     | Type              | Label | Description     |
|-----------|-------------------|-------|-----------------|
| key       | [string](#string) |       | Short key       |
| name      | [string](#string) |       | Description URL |
| is_active | [bool](#bool)     |       | Key flag        |

<a name="shortener-v1-UpdateUrlResponse"></a>

### UpdateUrlResponse

| Field | Type              | Label | Description     |
|-------|-------------------|-------|-----------------|
| ok    | [string](#string) |       | response result |

<a name="shortener-v1-ShortenerService"></a>

### ShortenerService

Service for shortening logic.

| Method Name    | Request Type                                                 | Response Type                                                  | Description                                             |
|----------------|--------------------------------------------------------------|----------------------------------------------------------------|---------------------------------------------------------|
| CreateShortUrl | [CreateShortUrlRequest](#shortener-v1-CreateShortUrlRequest) | [CreateShortUrlResponse](#shortener-v1-CreateShortUrlResponse) | Used to create short key for original URL.              |
| ResolveKey     | [ResolveKeyRequest](#shortener-v1-ResolveKeyRequest)         | [ResolveKeyResponse](#shortener-v1-ResolveKeyResponse)         | Used to get original URL by short key.                  |
| UpdateUrl      | [UpdateUrlRequest](#shortener-v1-UpdateUrlRequest)           | [UpdateUrlResponse](#shortener-v1-UpdateUrlResponse)           | Used to update information for URL entity by short key. |
| DeleteUrl      | [DeleteUrlRequest](#shortener-v1-DeleteUrlRequest)           | [DeleteUrlResponse](#shortener-v1-DeleteUrlResponse)           | Used to delete short key.                               |

<a name="user_urls_v1_user_urls-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## user_urls/v1/user_urls.proto

User urls related messages.

<a name="user_urls-v1-GetUserUrlsRequest"></a>

### GetUserUrlsRequest

| Field   | Type            | Label | Description |
|---------|-----------------|-------|-------------|
| limit   | [int32](#int32) |       |             |
| last_id | [int32](#int32) |       |             |

<a name="user_urls-v1-GetUserUrlsResponse"></a>

### GetUserUrlsResponse

| Field | Type                             | Label    | Description  |
|-------|----------------------------------|----------|--------------|
| items | [UserUrl](#user_urls-v1-UserUrl) | repeated | UserUrl data |
| count | [int32](#int32)                  |          | Urls count   |

<a name="user_urls-v1-UserUrl"></a>

### UserUrl

| Field        | Type                                                    | Label | Description     |
|--------------|---------------------------------------------------------|-------|-----------------|
| key          | [string](#string)                                       |       | Short key       |
| target_url   | [string](#string)                                       |       | Original URL    |
| name         | [string](#string)                                       |       | Description URL |
| clicks_count | [int32](#int32)                                         |       | Click amount    |
| is_active    | [bool](#bool)                                           |       | Key flag        |
| created_at   | [google.protobuf.Timestamp](#google-protobuf-Timestamp) |       | Created time    |
| last_used    | [google.protobuf.Timestamp](#google-protobuf-Timestamp) |       | Last used time  |

<a name="user_urls-v1-UserUrlsService"></a>

### UserUrlsService

Service for user urls logic.

| Method Name | Request Type                                           | Response Type                                            | Description                |
|-------------|--------------------------------------------------------|----------------------------------------------------------|----------------------------|
| GetUserUrls | [GetUserUrlsRequest](#user_urls-v1-GetUserUrlsRequest) | [GetUserUrlsResponse](#user_urls-v1-GetUserUrlsResponse) | Used to get all user urls. |

## Scalar Value Types

| .proto Type                    | Notes                                                                                                                                           | C++    | Java       | Python      | Go      | C#         | PHP            | Ruby                           |
|--------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|--------|------------|-------------|---------|------------|----------------|--------------------------------|
| <a name="double" /> double     |                                                                                                                                                 | double | double     | float       | float64 | double     | float          | Float                          |
| <a name="float" /> float       |                                                                                                                                                 | float  | float      | float       | float32 | float      | float          | Float                          |
| <a name="int32" /> int32       | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint32 instead. | int32  | int        | int         | int32   | int        | integer        | Bignum or Fixnum (as required) |
| <a name="int64" /> int64       | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint64 instead. | int64  | long       | int/long    | int64   | long       | integer/string | Bignum                         |
| <a name="uint32" /> uint32     | Uses variable-length encoding.                                                                                                                  | uint32 | int        | int/long    | uint32  | uint       | integer        | Bignum or Fixnum (as required) |
| <a name="uint64" /> uint64     | Uses variable-length encoding.                                                                                                                  | uint64 | long       | int/long    | uint64  | ulong      | integer/string | Bignum or Fixnum (as required) |
| <a name="sint32" /> sint32     | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int32s.                            | int32  | int        | int         | int32   | int        | integer        | Bignum or Fixnum (as required) |
| <a name="sint64" /> sint64     | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int64s.                            | int64  | long       | int/long    | int64   | long       | integer/string | Bignum                         |
| <a name="fixed32" /> fixed32   | Always four bytes. More efficient than uint32 if values are often greater than 2^28.                                                            | uint32 | int        | int         | uint32  | uint       | integer        | Bignum or Fixnum (as required) |
| <a name="fixed64" /> fixed64   | Always eight bytes. More efficient than uint64 if values are often greater than 2^56.                                                           | uint64 | long       | int/long    | uint64  | ulong      | integer/string | Bignum                         |
| <a name="sfixed32" /> sfixed32 | Always four bytes.                                                                                                                              | int32  | int        | int         | int32   | int        | integer        | Bignum or Fixnum (as required) |
| <a name="sfixed64" /> sfixed64 | Always eight bytes.                                                                                                                             | int64  | long       | int/long    | int64   | long       | integer/string | Bignum                         |
| <a name="bool" /> bool         |                                                                                                                                                 | bool   | boolean    | boolean     | bool    | bool       | boolean        | TrueClass/FalseClass           |
| <a name="string" /> string     | A string must always contain UTF-8 encoded or 7-bit ASCII text.                                                                                 | string | String     | str/unicode | string  | string     | string         | String (UTF-8)                 |
| <a name="bytes" /> bytes       | May contain any arbitrary sequence of bytes.                                                                                                    | string | ByteString | str         | []byte  | ByteString | string         | String (ASCII-8BIT)            |


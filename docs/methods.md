# Методы Edits и аналитики Reels

Каталог описывает конкретную сборку APK 448.0.0.53.84. Тип query/mutation у записей без контракта может быть определён по имени.

[Уровни доказательств](verification.md). Наличие operation ID не гарантирует доступность на сервере.

## Подробно разобранные методы

| Метод | Уровень | Назначение |
|---|---|---|
| [BaselAccountLevelInsightsQuery](methods/BaselAccountLevelInsightsQuery.md) | `live-verified` | Сводная аналитика аккаунта, с опциональными временными рядами. |
| [BaselAccountLevelReelsQuery](methods/BaselAccountLevelReelsQuery.md) | `live-verified` | Постраничный список Reels аккаунта, сортировка по метрикам, в том числе по пропускам. |
| [BaselAudienceInsightsQuery](methods/BaselAudienceInsightsQuery.md) | `live-verified` | Аналитика аудитории аккаунта с учётом периода и часового пояса. |
| [BaselKitClearDefaultMutation](methods/BaselKitClearDefaultMutation.md) | `static-contract` | Снять назначение набора по умолчанию. |
| [BaselKitCreateMutation](methods/BaselKitCreateMutation.md) | `static-contract` | Создание набора элементов. Изменяет данные аккаунта. |
| [BaselKitDeleteMutation](methods/BaselKitDeleteMutation.md) | `static-contract` | Удаление набора элементов. |
| [BaselKitSetDefaultMutation](methods/BaselKitSetDefaultMutation.md) | `static-contract` | Установить набором по умолчанию. |
| [BaselKitUpdateMutation](methods/BaselKitUpdateMutation.md) | `static-contract` | Обновление набора элементов. Изменяет данные аккаунта. |
| [BaselKitsQuery](methods/BaselKitsQuery.md) | `live-verified` | Чтение наборов переиспользуемых элементов Edits. |
| [BaselPublicInsightsQuery](methods/BaselPublicInsightsQuery.md) | `live-verified` | Публичная сокращённая статистика Reel. Не доказана как источник авторского графика удержания. |
| [BaselReelDetailsQuery](methods/BaselReelDetailsQuery.md) | `live-verified` | Детальная авторская аналитика Reel, включая числовые точки удержания. Основной найденный метод для исходной задачи. |
| [ReelInsightsQuery](methods/ReelInsightsQuery.md) | `live-verified` | Альтернативная ветка аналитики Reels в общем коде Instagram. Не доказано, что экран Edits использует именно её. |
| [XIGBaselAccountLevelReelsDataDeltaQuery](methods/XIGBaselAccountLevelReelsDataDeltaQuery.md) | `live-verified` | Пакетное обновление метрик выбранных Reels. |
| [XIGBaselInsightsCommentsQuery](methods/XIGBaselInsightsCommentsQuery.md) | `live-verified` | Аналитика комментариев выбранного Reel. |
| [XIGBaselInsightsRetentionSummaryMutation](methods/XIGBaselInsightsRetentionSummaryMutation.md) | `static-contract` | Генерация текстового разбора удержания и hook analysis. Это отдельный вызов, не массив точек графика. |

## Остальные операции с именами Basel / Eddy

У этих записей может отсутствовать контракт. Не подставляйте параметры по предположению. Полный машинный реестр: [operations.json](../src/edits_api/operations.json).

| Operation | Kind | client_doc_id | Evidence |
|---|---|---|---|
| `BaselCreateStickyMutation` | mutation | `146269550813467008709332678698` | static-reference |
| `BaselCreatorChannelContentQuery` | query | `338493678912973121533757805434` | static-reference |
| `BaselCreatorChannelsQuery` | query | `15139020088074941112053393368` | static-reference |
| `BaselFetchStickiesQuery` | query | `21367069567577771743497930351` | static-reference |
| `BaselHideCollectionMutation` | mutation | `144182739914969512573623756964` | static-reference |
| `BaselInspirationTypeaheadSearchQuery` | query | `36773660617222846870492614464` | static-reference |
| `BaselQuickPreviewQuery` | query | `21112752869082033502176644045` | static-reference |
| `BaselReframeFetchMediaQuery` | query | `39107432471651866333453962911` | static-reference |
| `BaselSendReelIdsQuery` | query | `127085002216487195239248035281` | static-reference |
| `BaselUnhideCollectionMutation` | mutation | `290713855117928426241922654236` | static-reference |
| `BaselUploadEditQuery` | query | `152692439015369647290146400126` | static-reference |
| `GetBaselOnboardingInfoQuery` | query | `33902372673317392047945990110` | static-reference |
| `ResetBaselOnboardingMutation` | mutation | `143962487615461026201602993924` | registry-only |
| `SetBaselOnboardingMutation` | mutation | `34399958464663015328171836228` | static-reference |
| `BaselAccountLevelInsightsQuery` | query | `279077652713939115792325780352` | live-verified |
| `BaselAccountLevelReelsQuery` | query | `11900819615835482353778696516` | live-verified |
| `BaselAppInstallOnboardedBFFsQueryQuery` | query | `324948423116457329790692969758` | static-reference |
| `BaselAppStickyNoteDeletionStatus` | not-inferred | `37953982910939554770791661338` | static-reference |
| `BaselAudienceInsightsQuery` | query | `416010146012703390907640345604` | live-verified |
| `BaselBatchSetUserInterestPreferences` | not-inferred | `400578367514659592934858223882` | static-reference |
| `BaselConvoStartersQuery` | query | `32924785613615245411984394618` | static-reference |
| `BaselCreateCaptionStyleMutation` | mutation | `22266339806216110982799019080` | static-reference |
| `BaselDeleteCaptionStyleMutation` | mutation | `26556804617791235260417052728` | static-reference |
| `BaselDeleteStickyMutation` | mutation | `12877971221803269183656149424` | static-reference |
| `BaselDeleteTextAndCaptionStyleAttributeMutation` | mutation | `40268265110284170882450073408` | static-reference |
| `BaselFetchCaptionStylesQuery` | query | `33206399363197650524836643351` | static-reference |
| `BaselFetchFontMetadataQuery` | query | `8716649898402109514706229531` | static-reference |
| `BaselFetchSuggestedStickiesQuery` | query | `28058430327383270614335116927` | static-reference |
| `BaselFetchTextAndCaptionStyleAttributesQuery` | query | `25514429893949653360627050280` | static-reference |
| `BaselFetchTextAssetRankingQuery` | query | `365618958110346245445670079631` | static-reference |
| `BaselFetchTextStylesQuery` | query | `35457592491215531464198299121` | static-reference |
| `BaselFetchUnifiedSavedItemsQuery` | query | `17708032196910104015691851755` | static-reference |
| `BaselFirstTimeRecommendedInterestsQuery` | query | `201608983515979075912614815395` | static-reference |
| `BaselGenAIInspirationalPromptQuery` | query | `407725084216358075567113229640` | static-reference |
| `BaselInspirationSearchAudioQuery` | query | `32527017309108467801305272622` | static-reference |
| `BaselInspirationSearchClipsQuery` | query | `39669305356572369118438404970` | static-reference |
| `BaselKitAddMemberMutation` | mutation | `381593069411413306612098671226` | registry-only |
| `BaselKitClearDefaultMutation` | mutation | `26572918775585087653645090328` | static-contract |
| `BaselKitCreateMutation` | mutation | `55935713910906349927979058123` | static-contract |
| `BaselKitDeleteMutation` | mutation | `359751225710120235276991625918` | static-contract |
| `BaselKitQuery` | query | `25203172192950179050102923575` | registry-only |
| `BaselKitSetDefaultMutation` | mutation | `227627550715913420820782541062` | static-contract |
| `BaselKitUpdateMutation` | mutation | `19437238033720027386254691847` | static-contract |
| `BaselKitsQuery` | query | `57198449616693595270598413994` | live-verified |
| `BaselPopularTopicsV2Query` | query | `12568638147687796215763485378` | static-reference |
| `BaselPublicInsightsQuery` | query | `32880071334541180518965887244` | live-verified |
| `BaselReelCarouselThumbnailsQuery` | query | `37793682035709244311952866661` | registry-only |
| `BaselReelDetailsQuery` | query | `3261342854360971614358769315` | live-verified |
| `BaselRemoveInterestPreference` | not-inferred | `279730435114630214776219557974` | static-reference |
| `BaselSetInterestPreference` | not-inferred | `264300213113279678871261328500` | static-reference |
| `BaselSuggestedStickiesSyncMutation` | mutation | `240389376913660919577363204460` | static-reference |
| `BaselUnsaveTextStyleMutation` | mutation | `31814063387276630937082298885` | static-reference |
| `BaselUpdateInterestPreference` | not-inferred | `21025592255358648086773248320` | static-reference |
| `BaselUpdateStickyMutation` | mutation | `38070547268019190588077637807` | static-reference |
| `BaselUpsertSaveTextStyleMutation` | mutation | `10798720533305745640740113624` | static-reference |
| `BaselUpsertTextAndCaptionStyleAttributeMutation` | mutation | `151156858811813990283557130615` | static-reference |
| `BaselUserInterestsQuery` | query | `3915367706765006873943462422` | static-reference |
| `EddyContextualSessionMutation` | mutation | `28918339075043295009754880816` | static-reference |
| `EddyContextualSessionVNextMutation` | mutation | `117088210715457252942779465515` | static-reference |
| `EddyInterruptSessionMutation` | mutation | `68254139015546697381844805319` | static-reference |
| `EddyInterruptStreamVNextMutation` | mutation | `4902065261429867164749611166` | static-reference |
| `EddyMessageCreateMutation` | mutation | `2537440596926965018587530838` | static-reference |
| `EddyMessagesListQuery` | query | `31212052255530774201974817322` | static-reference |
| `EddyMessagesSubscription` | subscription-name-unverified | `173100433417284885772646475302` | static-reference |
| `EddyMessagesVNextSubscription` | subscription-name-unverified | `23087025310731926163510292689` | static-reference |
| `EddyOILAssetDeleteMutation` | mutation | `205547665413262698642135930599` | static-reference |
| `EddySendMessageVNextMutation` | mutation | `355492009414373797281346876689` | static-reference |
| `EddyThreadCreateMutation` | mutation | `38042966744791913026491322262` | static-reference |
| `EddyThreadDeleteMutation` | mutation | `27895876791156476409552919836` | static-reference |
| `EddyThreadDeleteVNextMutation` | mutation | `35134503665120432686908495885` | static-reference |
| `EddyThreadMarkSeenMutation` | mutation | `16984999661583293458646143189` | static-reference |
| `EddyThreadUpdateNameMutation` | mutation | `10347044879860543944965476693` | static-reference |
| `EddyThreadUpdateNameVNextMutation` | mutation | `203998410817469549358997399167` | static-reference |
| `EddyThreadsListQuery` | query | `18469122695810201494622847926` | static-reference |
| `EddyThreadsListVNextQuery` | query | `20590092027253678097626624804` | static-reference |
| `EddyTurnFeedbackMutation` | mutation | `167928175915362825339938636674` | static-reference |
| `EddyUnseenSessionCountMutation` | mutation | `233394063910712271613182243972` | static-reference |
| `EddyVNextHistoryQuery` | query | `18277663048779488289358638489` | static-reference |
| `IGSearchSerpDeliveryBaselineQuery` | query | `320955831910256781982931603333` | registry-only |
| `NMEGAIBaselQuotaQuery` | query | `236959384011218202348087766269` | registry-only |
| `NMEGAIBaselSubscriptionQuery` | query | `10748361825258383857593355085` | static-reference |
| `SaveBaselReframeElementMutation` | mutation | `19604600844375373728835386372` | static-reference |
| `UnsaveBaselReframeElementMutation` | mutation | `97539861911428219167129448826` | static-reference |
| `XIGBaselAccountLevelCommentsQuery` | query | `11102125853857433107054303616` | static-reference |
| `XIGBaselAccountLevelReelsDataDeltaQuery` | query | `15638181364556178962628739248` | live-verified |
| `XIGBaselInsightsAccountLevelQuery` | query | `106742138712043730756309692905` | static-reference |
| `XIGBaselInsightsCommentsQuery` | query | `29719058955793752815580108112` | live-verified |
| `XIGBaselInsightsRetentionSummaryMutation` | mutation | `26704303781083176767119591657` | static-contract |

PRODUCT_PLATFORM := tone
$(call inherit-product, vendor/nxp/nxp-vendor.mk)
$(call inherit-product, vendor/qcom/prebuilt/qcom-vendor.mk)
$(call inherit-product, vendor/sony/tone-common/tone-partial.mk)
$(call inherit-product, $(LOCAL_PATH)/keyaki-partial.mk)

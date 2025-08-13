# becusengenhariaservidor

# COPA = "1DDWybRj41BYbQgN4zXhYctUurZQ6sLN5"
# SUPER = "1suuLWnTVjvNYVB6B3yBfyBWw2Hz5qrUu"
# SPL = "1OZmW6tj6JEhSpvGRW0vU-N29JSZq1Vde"
# CPL = "1EWknyko-NmM38UPcnyfIbxRPPRVatWXA"
# CSJ = "1QZOtXaVIcpgP4sYlT_a3FNOxv80r5xZS"
# CJD = "1t6xUZmq7MwJtPCZIU2nt_g8sUHdORBkt"
# CCS = "1nZCUgKFIzWlM2aaJbE0zQ79CMiA_wavU"
# CCP = "1qy4im__dp5LXPDuKAZCp7kYpoQLdka7X"
# CBS =  "1pG5xYnjlTiZLXAYRWwJA3fbJIK5pWe-V"
# CBR = "1cUFXXQTHV32zWx42jwLbErgnaEnuut1p"


# servidor.becus

PROJETOS = "1-h_XNyGy3EtbFm5T0aqbK-ljpzJxecfi"
SPL = "1pNj093dKiURsAKungx5MUkFjXg7inkny"
SES = '1gn4F2OfR5RTva4OqHo2hAHEYi7r4m_GK'
SLD = "1aBZkXjzX1ax4YLeVx-_Uax9C3VqaKEuU"
SMA = "171ByhCGc1o3YuQT7O0wDXPN8f9RSA69w"
CPL = "1K3rkmwkygs_EcuJcmW6W8XuSwZa6aZ9-"
CCP = "1kdoXFnnA8hTiGD01g_ywHZVr2vdBWVgN"
CBR = "1-X5IMz_8q3KpLCqA1E9m8jv5O_LTuTlm"
CBS = "1MM4pyS1IU9-QrLybwddxBS2DQZRqPBE8"
CJD = "19cXrK3oy1XhW-r5Vw8d9U00TLsZYL4ho"
CSJ = "1eu0e_5Ahe07rkC7G0_LV9PCHHkzIYoz7"
CCS = "1Igwyrq0UDwK8pk-b6ToG-2eELTieMIgj"


def get_drive_folder_id(name):
    name = name.lower()
    if "cpl" in name:
        return CPL
    if "spl" in name:
        return SPL
    if "ses" in name:
        return SES
    if "sld" in name:
        return SLD
    if "sma" in name:
        return SMA
    if "csj" in name:
        return CSJ
    if "cjd" in name:
        return CJD
    if "ccs" in name:
        return CCS
    if "ccp" in name:
        return CCP
    if "cbs" in name:
        return CBS
    if "cbr" in name:
        return CBR
    return None  # Ou você pode levantar uma exceção se preferir
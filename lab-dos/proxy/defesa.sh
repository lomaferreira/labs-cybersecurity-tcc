#!/bin/sh
set -eu

config_ativa=/etc/nginx/conf.d/default.conf
config_defesa=/opt/defesa/ativa.conf
config_sem_defesa=/opt/defesa/desativada.conf
app_url=http://app-dos:5000

if [ "$#" -ne 1 ]; then
    echo "Uso: defesa ativar|desativar" >&2
    exit 2
fi

trocar_configuracao() {
    nova_configuracao=$1
    anterior=$(mktemp)
    cp "$config_ativa" "$anterior"

    if ! cp "$nova_configuracao" "$config_ativa"; then
        cp "$anterior" "$config_ativa"
        rm -f "$anterior"
        echo "Erro: não foi possível instalar a configuração do Nginx." >&2
        return 1
    fi

    if ! nginx -t; then
        cp "$anterior" "$config_ativa"
        nginx -t
        rm -f "$anterior"
        echo "Erro: configuração inválida; a configuração anterior foi restaurada." >&2
        return 1
    fi

    if ! nginx -s reload; then
        cp "$anterior" "$config_ativa"
        nginx -t
        nginx -s reload
        rm -f "$anterior"
        echo "Erro: falha ao recarregar Nginx; configuração anterior restaurada." >&2
        return 1
    fi

    rm -f "$anterior"
}

case "$1" in
    ativar)
        curl --fail --silent --show-error --max-time 5 \
            -X POST "$app_url/admin/ativar_defesa"
        if ! trocar_configuracao "$config_defesa"; then
            if ! curl --fail --silent --show-error --max-time 5 \
                -X POST "$app_url/admin/desativar_defesa"; then
                echo "A defesa do Flask pode continuar ativa; verifique /admin/status." >&2
            fi
            exit 1
        fi
        printf '\nDefesas do Flask e do Nginx ativadas.\n'
        ;;
    desativar)
        trocar_configuracao "$config_sem_defesa"
        curl --fail --silent --show-error --max-time 5 \
            -X POST "$app_url/admin/desativar_defesa"
        printf '\nDefesas do Flask e do Nginx desativadas.\n'
        ;;
    *)
        echo "Uso: defesa ativar|desativar" >&2
        exit 2
        ;;
esac

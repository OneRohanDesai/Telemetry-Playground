{{- define "telemetry.name" -}}
telemetry-playground
{{- end }}

{{- define "telemetry.namespace" -}}
{{ .Values.namespace | default "telemetry" }}
{{- end }}

{{- define "telemetry.labels" -}}
app.kubernetes.io/name: {{ include "telemetry.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: Helm
{{- end }}

{{/*
Standard Kubernetes labels following app.kubernetes.io conventions
*/}}

{{- define "todo-app.standard-labels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/component: {{ .Values.component | default "application" }}
app.kubernetes.io/part-of: {{ .Chart.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "todo-app.match-labels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "todo-app.backend-labels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}-backend
app.kubernetes.io/instance: {{ .Release.Name }}-backend
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/component: backend
app.kubernetes.io/part-of: {{ include "todo-app.name" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
ai/managed: "true"
ai/type: "backend"
ai/discoverable: "true"
{{- end }}

{{- define "todo-app.backend-match-labels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}-backend
app.kubernetes.io/instance: {{ .Release.Name }}-backend
{{- end }}

{{- define "todo-app.frontend-labels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}-frontend
app.kubernetes.io/instance: {{ .Release.Name }}-frontend
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/component: frontend
app.kubernetes.io/part-of: {{ include "todo-app.name" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
ai/managed: "true"
ai/type: "frontend"
ai/discoverable: "true"
{{- end }}

{{- define "todo-app.frontend-match-labels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}-frontend
app.kubernetes.io/instance: {{ .Release.Name }}-frontend
{{- end }}

{{- define "todo-app.database-labels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}-database
app.kubernetes.io/instance: {{ .Release.Name }}-database
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/component: database
app.kubernetes.io/part-of: {{ include "todo-app.name" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
ai/managed: "true"
ai/type: "database"
ai/discoverable: "true"
{{- end }}

{{- define "todo-app.database-match-labels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}-database
app.kubernetes.io/instance: {{ .Release.Name }}-database
{{- end }}
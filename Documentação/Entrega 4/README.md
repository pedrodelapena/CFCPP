# Projeto - Entrega 4

Esta etapa do projeto consiste dividir um arquivo em pacotes menores, facilitando a transmissão, a detecção de bits corrompidos e o consequente reenvio apenas dos pacotes corrompidos. A detecção de bits corrompidos ocorre pela implementação do CRC (Cyclic redundancy
 check) tanto no Head quanto no Payload.
Para que a transmissão seja realizada, o servidor compara os CRCs e envia um ACK para o client caso o pacote esteja de acordo com o esperado ou um nACK, caso contrário.
 
## Fragmentação




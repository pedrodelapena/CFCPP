# Projeto - Entrega 4

Esta etapa do projeto consiste dividir um arquivo em pacotes menores, facilitando a transmissão, a detecção de bits corrompidos e o consequente reenvio apenas dos pacotes corrompidos. A detecção de bits corrompidos ocorre pela implementação do CRC (Cyclic redundancy
 check) tanto no Head quanto no Payload.
<p>Para que a transmissão seja realizada, o servidor compara os CRCs e envia um ACK para o client caso o pacote esteja de acordo com o esperado ou um nACK, caso contrário.</p>
 
## Fragmentação

Nesta etapa, o payload é dividido em vários pacotes com <b>tamanho máximo</b> de 2048 bytes. A divisão faz com que:

<p>- O tempo da tranmissão torne-se menor devido à redução no tamanho dos pacotes, possibilitando que arquivos maiores, quando corrompidos, sejam mais facilmente corrigidos.</p>
<p>- O <i>Overhead</i> e consequentemente <i>Throughput</i> tornem-se maiores e o mesmo ocorre com a velocidade de transmissão dos dados. </p>
<p>- O payload não extrapole o tamanho máximo nos campos do Head, isto é, o tamanho pré definido garante que o número não passará de 16 bits e possibilita a formação bem sucedida do Head.</p>

## Head

Previamente, o Head continha apenas os campos:

start (8 bits), size (16 bits), SYN (8 bits), ACK/nACK (8 bits)

Nesta etapa do projeto, foram adicionados os seguintes campos ao Head:

P_size (8 bits), P_total (8 bits), CheckSum (16 bits), CheckSum_head (16 bits),

onde P_size é o tamanho do pacote, P_total é o tamanho total dos pacotes, CheckSum_head é o CRC calculado para o Head e o CheckSum é o CRC calculado para o Payload.

## Polinômio utilizado para o CRC

O polinômio utilizado foi o CRC-16-IBM, também conhecido apenas como <b>CRC-16</b>. 


| Forma do polinômio | Conteudo    |
|-------------|--------------------|
| Hexadecimal |         0x18005    |
| Binária     |  11000000000000101 |
| Polinomial  | x^16+x^15+x^12+x^0 |

#version 330 core

in vec3 vColor;
in vec2 TexCoord;

out vec4 FragColor;

uniform sampler2D textura1;

void main(){
    // FragColor = texture(textura1, TexCoord) * vec4(vColor, 1.0);
    // Se a coordenada UV for (0,0), assume-se que é uma lateral sem textura
    if (TexCoord.x <= 0.001 && TexCoord.y <= 0.001) {
        FragColor = vec4(vColor, 1.0); // Cor pura nas laterais
    } else {
        // Mistura a textura com a cor do topo
        vec4 texColor = texture(textura1, TexCoord);
        FragColor = vec4(texColor.rgb * vColor, 1.0); 
    }
}
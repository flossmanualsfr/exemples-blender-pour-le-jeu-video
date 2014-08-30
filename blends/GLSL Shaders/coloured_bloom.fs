uniform sampler2D bgl_RenderedTexture;
int NSAMPLES = 12;
float blur = 0.001;


void main(void) {
    vec3 texblur = vec3(0.0);
    vec3 TEXTURE = texture2D(bgl_RenderedTexture, gl_TexCoord[0].st).rgb;
    for (int i = -NSAMPLES; i < NSAMPLES; ++i) {
        texblur += texture2D(bgl_RenderedTexture, vec2(gl_TexCoord[0].x-(i*blur), gl_TexCoord[0].y)).rgb/NSAMPLES;
        texblur += texture2D(bgl_RenderedTexture, vec2(gl_TexCoord[0].x, gl_TexCoord[0].y-(i*blur))).rgb/NSAMPLES;
        texblur += texture2D(bgl_RenderedTexture, vec2(gl_TexCoord[0].x-(i*blur), gl_TexCoord[0].y-(i*blur))).rgb/NSAMPLES;
        texblur += texture2D(bgl_RenderedTexture, vec2(gl_TexCoord[0].x+(i*blur), gl_TexCoord[0].y-(i*blur))).rgb/NSAMPLES;      
        };              
    vec3 lum = texblur;
    lum -= 1.8;
    lum *= lum*lum;
    vec3 stencil = max(lum , 0.0);          
       
    gl_FragColor = vec4(TEXTURE+(stencil/70), 1.0);
}

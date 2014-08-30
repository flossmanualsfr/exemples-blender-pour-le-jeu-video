uniform sampler2D bgl_RenderedTexture;
int NSAMPLES = 12;
float blur = 0.001;
float gain = 4.0;


void main(void) {
    float texr = 0.0;
    float texg = 0.0;
    float texb = 0.0;
    vec3 texblur = vec3(0.0);
    vec3 TEXTURE = texture2D(bgl_RenderedTexture, gl_TexCoord[0].st).rgb;
   
    for (int i = -NSAMPLES; i < NSAMPLES; ++i) {
        texr += texture2D(bgl_RenderedTexture, vec2(gl_TexCoord[0].x-(i*blur) + (blur*4), gl_TexCoord[0].y)).r/NSAMPLES;
        texg += texture2D(bgl_RenderedTexture, vec2(gl_TexCoord[0].x-(i*blur), gl_TexCoord[0].y)).g/NSAMPLES;
        texb += texture2D(bgl_RenderedTexture, vec2(gl_TexCoord[0].x-(i*blur) - (blur*4), gl_TexCoord[0].y)).b/NSAMPLES;             
        texblur += texture2D(bgl_RenderedTexture, vec2(gl_TexCoord[0].x-(i*blur), gl_TexCoord[0].y-(i*blur))).rgb/NSAMPLES;
        texblur += texture2D(bgl_RenderedTexture, vec2(gl_TexCoord[0].x+(i*blur), gl_TexCoord[0].y-(i*blur))).rgb/NSAMPLES;    
        };
         
    vec3 chroma = vec3(texr, texg, texb)-1.0;                
    vec3 lum = (texblur/2+chroma);
    vec3 stencil = max(lum , 0.0);        
     
    gl_FragColor = vec4(TEXTURE+stencil/gain, 1.0);
}

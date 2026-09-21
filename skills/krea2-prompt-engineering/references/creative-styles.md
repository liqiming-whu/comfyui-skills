# 创作风格模板

仅在用户明确提出对应风格时使用。模板是风格段基线，不用于覆盖用户已经提供的美术方向；用户指定其他风格时，依据其关键词合理补全即可。最终提示词按用户指定语言或请求语言统一输出：中文提示词应将模板准确译成中文，英文提示词保留英文，不把两种语言拼接在同一提示词中。

## 写实照片

```text
Natural realistic photography, authentic body proportions, natural skin texture.
```

中文表达：自然写实的摄影风格，真实的身体比例，自然的皮肤质感。

> `authentic body proportions` 是一根**幅度钳制器**：它把输出拉回「比例自然」那个吸引子。做局部形态校准或分档时，它会把档距压小但让结果更稳；想拉开局部形态幅度就删掉它（`Natural realistic photography, natural skin texture, candid photography.`），想收敛、防过执行就保留。删它是单变量改动，会同时改变幅度，比较时要单独记一笔。

## 写实绘画

```text
Realistic painterly digital illustration, subtle visible brushwork, natural painterly shading, detailed lace and hair texture, cinematic color grading, tasteful presentation.
```

中文表达：写实绘画感的数字插画，细微可见的笔触，自然的绘画式明暗塑造，细致的蕾丝与发丝纹理，电影感调色，克制得体的呈现。

## 半写实

```text
High-quality semi-realistic anime illustration, polished character key art, delicate shading, detailed lace and hair texture, cinematic color grading, tasteful presentation.
```

中文表达：高质量半写实动漫插画，精致的角色主视觉，细腻明暗，细致的蕾丝与发丝纹理，电影感调色，克制得体的呈现。

## 二次元

```text
High-quality polished 2D anime illustration, clean expressive line art, refined cel shading, luminous sunset rim light, detailed wet hair and fabric rendering, sophisticated adult character design, cinematic warm color palette, tasteful resort fashion key art.
```

中文表达：高质量精修二维动漫插画，干净而富有表现力的线稿，精细赛璐璐上色，明亮的日落轮廓光，细致的湿发与面料表现，成熟精致的成年角色设计，电影感暖色调，克制得体的度假时尚主视觉。

## 使用规则

- 用户明确说“写实照片”“写实绘画”“半写实”或“二次元”时，使用对应模板作为风格段，并让场景光线与其一致。
- 模板中的具体细节可被用户要求覆盖。例如用户指定阴天冷调时，不保留二次元模板的日落暖光；用户指定干发时，不保留 wet hair。
- 用户未指定风格时不添加这些模板。用户指定模板外的风格时，保留其风格名称并补充少量媒介、笔触或光影特征，不强行归入四类。
- 角色 LoRA 触发词仍位于整条提示词开头；风格段通常放在场景、构图和光线之后，**不得排在核心形态句之前**（风格句自带体型先验，抢在前面会压掉核心形态）。

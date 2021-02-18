from forthpie.model import *

def test_UserVariable_init_no_cells_arg():
    uv = UserVariable("foo")

    assert uv.cells == 1

def test_UserVariable_init_with_cells_arg():
    uv = UserVariable("foo", cells=2)

    assert uv.cells == 2

def test_WordSet_user_variables():
    uvs = [UserVariable("uv1"), UserVariable("uv2")]
    ws = WordsSet("foo",
        *uvs,
        ColonWord("cw", []),
        Primitive("p"))

    assert ws.user_variables == uvs

def test_WordSet_primitives():
    prims = [Primitive("p1"), Primitive("p2")]
    ws = WordsSet("foo",
        *prims,
        ColonWord("cw", []),
        UserVariable("uv"))

    assert ws.primitives == prims

def test_WordSet_colon_words():
    cw = [ColonWord("w1", []), ColonWord("w2", [])]
    ws = WordsSet("foo",
        *cw,
        Primitive("p"),
        UserVariable("uv"))

    assert ws.colon_words == cw

def test_Image_user_variables():
    ws1 = WordsSet("ws1",
        UserVariable("u1"),
        ColonWord("c1", []))
    ws2 = WordsSet("ws2",
        Primitive("p1"),
        UserVariable("u2"),
        UserVariable("u3"))
    ws3 = WordsSet("ws3",
        ColonWord("c2", []),
        ColonWord("c3", []))
    image = Image(
        ws1, ws2, ws3
    )
    assert image.user_variables == ws1.user_variables + ws2.user_variables + ws3.user_variables

def test_Image_primitives():
    ws1 = WordsSet("ws1",
        UserVariable("u1"),
        ColonWord("c1", []))
    ws2 = WordsSet("ws2",
        Primitive("p1"),
        UserVariable("u2"),
        UserVariable("u3"))
    ws3 = WordsSet("ws3",
        ColonWord("c2", []),
        ColonWord("c3", []))
    image = Image(
        ws1, ws2, ws3
    )
    assert image.primitives == ws1.primitives + ws2.primitives + ws3.primitives

def test_Image_colon_words():
    ws1 = WordsSet("ws1",
        UserVariable("u1"),
        ColonWord("c1", []))
    ws2 = WordsSet("ws2",
        Primitive("p1"),
        UserVariable("u2"),
        UserVariable("u3"))
    ws3 = WordsSet("ws3",
        ColonWord("c2", []),
        ColonWord("c3", []))
    image = Image(
        ws1, ws2, ws3
    )
    assert image.colon_words == ws1.colon_words + ws2.colon_words + ws3.colon_words